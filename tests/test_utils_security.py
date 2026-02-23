import sys
import os
import unittest
from unittest.mock import MagicMock

# 1. Mock streamlit BEFORE importing utils
mock_st = MagicMock()

# Configure cache_resource to be a transparent decorator
def mock_cache_resource(func=None, **kwargs):
    if func is not None:
        return func
    def wrapper(f):
        return f
    return wrapper

mock_st.cache_resource.side_effect = mock_cache_resource
sys.modules['streamlit'] = mock_st

# 2. Mock gspread BEFORE importing utils
mock_gspread = MagicMock()

# Configure gspread exceptions to be real classes
class MockSpreadsheetNotFound(Exception):
    pass

mock_gspread.exceptions.SpreadsheetNotFound = MockSpreadsheetNotFound
sys.modules['gspread'] = mock_gspread

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 3. Now import utils
import utils

class TestVulnerability(unittest.TestCase):
    def setUp(self):
        mock_st.reset_mock()
        mock_gspread.reset_mock()
        # Ensure secrets are set
        mock_st.secrets = {"gcp_service_account": {"some": "creds"}}

    def test_get_db_connection_security(self):
        """Test that get_db_connection does not leak sensitive errors."""
        sensitive_msg = "SENSITIVE_CONNECTION_ERROR"
        mock_gspread.service_account_from_dict.side_effect = Exception(sensitive_msg)

        utils.get_db_connection()

        self.assert_generic_error(sensitive_msg, "An unexpected error occurred while connecting to Google Sheets. Please check the logs.")

    def test_add_transaction_security(self):
        """Test that add_transaction does not leak sensitive errors."""
        # Mock get_db_connection to return a valid worksheet
        mock_worksheet = MagicMock()
        mock_gspread.service_account_from_dict.return_value.open.return_value.sheet1 = mock_worksheet

        # Mock append_row to raise exception
        sensitive_msg = "SENSITIVE_WRITE_ERROR"
        mock_worksheet.append_row.side_effect = Exception(sensitive_msg)

        tx_data = {"ID": "123", "Amount": 100}
        utils.add_transaction(tx_data)

        self.assert_generic_error(sensitive_msg, "An error occurred while saving to Google Sheets. Please check the logs.")

    def test_delete_transaction_security(self):
        """Test that delete_transaction does not leak sensitive errors."""
        # Mock get_db_connection to return a valid worksheet
        mock_worksheet = MagicMock()
        mock_gspread.service_account_from_dict.return_value.open.return_value.sheet1 = mock_worksheet

        # Mock get_all_records to raise exception
        sensitive_msg = "SENSITIVE_READ_ERROR"
        mock_worksheet.get_all_records.side_effect = Exception(sensitive_msg)

        utils.delete_transaction(["123"])

        self.assert_generic_error(sensitive_msg, "An error occurred while deleting from Google Sheets. Please check the logs.")

    def assert_generic_error(self, sensitive_msg, expected_generic_msg):
        # Check that st.error was NOT called with the sensitive message
        for call in mock_st.error.call_args_list:
            args, _ = call
            error_msg = str(args[0])
            if sensitive_msg in error_msg:
                self.fail(f"Vulnerability FOUND: st.error called with sensitive message: {error_msg}")

        # Check that st.error WAS called with the generic message
        mock_st.error.assert_called_with(expected_generic_msg)

if __name__ == '__main__':
    unittest.main()
