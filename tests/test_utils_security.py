import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# conftest.py (loaded first by pytest) has already patched sys.modules['streamlit']
# and imported utils. We import utils here to get the same cached module so that
# utils.st refers to the conftest mock (the one under test).
import utils


class TestVulnerability(unittest.TestCase):
    def setUp(self):
        # Reset the streamlit mock that utils.st points to (conftest's mock_st).
        utils.st.reset_mock()
        # Restore a minimal secrets dict so get_db_connection can reach the gspread call.
        utils.st.secrets = {"gcp_service_account": {"some": "creds"}}

    def test_get_db_connection_security(self):
        """get_db_connection must not expose raw exception details in st.error."""
        sensitive_msg = "SENSITIVE_CONNECTION_ERROR"

        # Use a distinct class for SpreadsheetNotFound so that a plain Exception
        # raised by service_account_from_dict falls through to the generic handler.
        class _MockSpreadsheetNotFound(Exception):
            pass

        with patch('utils.gspread') as mock_gspread:
            mock_gspread.exceptions.SpreadsheetNotFound = _MockSpreadsheetNotFound
            mock_gspread.service_account_from_dict.side_effect = Exception(sensitive_msg)
            utils.get_db_connection()

        self.assert_generic_error(
            sensitive_msg,
            "An unexpected error occurred while connecting to Google Sheets. Please check the logs.",
        )

    def test_add_transaction_security(self):
        """add_transaction must not expose raw exception details in st.error."""
        sensitive_msg = "SENSITIVE_WRITE_ERROR"
        mock_worksheet = MagicMock()
        mock_worksheet.append_row.side_effect = Exception(sensitive_msg)

        with patch('utils.get_db_connection', return_value=mock_worksheet):
            utils.add_transaction({"ID": "123", "Amount": 100})

        self.assert_generic_error(
            sensitive_msg,
            "An error occurred while saving to Google Sheets. Please check the logs.",
        )

    def test_delete_transaction_security(self):
        """delete_transaction must not expose raw exception details in st.error."""
        sensitive_msg = "SENSITIVE_READ_ERROR"
        mock_worksheet = MagicMock()
        mock_worksheet.get_all_records.side_effect = Exception(sensitive_msg)

        with patch('utils.get_db_connection', return_value=mock_worksheet):
            utils.delete_transaction(["123"])

        self.assert_generic_error(
            sensitive_msg,
            "An error occurred while deleting from Google Sheets. Please check the logs.",
        )

    def assert_generic_error(self, sensitive_msg, expected_generic_msg):
        """Assert that st.error was called with the generic message, not the sensitive one."""
        for call in utils.st.error.call_args_list:
            args, _ = call
            error_msg = str(args[0])
            if sensitive_msg in error_msg:
                self.fail(
                    f"Vulnerability FOUND: st.error called with sensitive message: {error_msg}"
                )

        utils.st.error.assert_called_with(expected_generic_msg)


if __name__ == '__main__':
    unittest.main()
