import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
import utils

# --- show_global_sidebar Tests ---

def test_show_global_sidebar_initializes_state(mock_streamlit):
    """Test that session state variables are initialized correctly."""
    mock_streamlit.session_state.clear()
    mock_streamlit.secrets = {"gemini_api_key": "secret_key"}

    # Ensure button returns False so we don't trigger "Add" logic
    mock_streamlit.button.return_value = False
    # Ensure selectbox returns a string
    mock_streamlit.sidebar.selectbox.return_value = "Default Family"
    # Ensure file_uploader returns None
    mock_streamlit.sidebar.file_uploader.return_value = None
    # Ensure text_input (for API Key) returns the current value so no update is triggered
    mock_streamlit.sidebar.text_input.return_value = "secret_key"

    utils.show_global_sidebar()

    assert "profiles" in mock_streamlit.session_state
    assert mock_streamlit.session_state["profiles"] == ["Default Family"]
    assert "active_profile" in mock_streamlit.session_state
    assert mock_streamlit.session_state["active_profile"] == "Default Family"
    assert "profile_pictures" in mock_streamlit.session_state
    assert mock_streamlit.session_state["profile_pictures"] == {}
    assert "gemini_api_key" in mock_streamlit.session_state
    assert mock_streamlit.session_state["gemini_api_key"] == "secret_key"

def test_show_global_sidebar_renders_ui(mock_streamlit):
    """Test that sidebar elements are rendered."""
    mock_streamlit.session_state.clear()
    mock_streamlit.secrets = {}
    mock_streamlit.button.return_value = False
    mock_streamlit.sidebar.selectbox.return_value = "Default Family"
    mock_streamlit.sidebar.file_uploader.return_value = None

    utils.show_global_sidebar()

    mock_streamlit.sidebar.title.assert_called_with("PIEZA Settings")
    mock_streamlit.sidebar.header.assert_any_call("User Profile")
    mock_streamlit.sidebar.selectbox.assert_called()
    mock_streamlit.sidebar.expander.assert_called_with("Add New Member")
    mock_streamlit.sidebar.file_uploader.assert_called()

def test_show_global_sidebar_add_member(mock_streamlit):
    """Test adding a new member via sidebar."""
    mock_streamlit.session_state.clear()
    mock_streamlit.session_state.update({
        "profiles": ["Default Family"],
        "active_profile": "Default Family",
        "profile_pictures": {},
        "gemini_api_key": ""
    })
    mock_streamlit.secrets = {}

    # Mock text input and button
    mock_streamlit.text_input.return_value = "New Member"
    mock_streamlit.button.return_value = True
    # We also need selectbox to behave
    mock_streamlit.sidebar.selectbox.return_value = "Default Family"
    mock_streamlit.sidebar.file_uploader.return_value = None

    utils.show_global_sidebar()

    assert "New Member" in mock_streamlit.session_state["profiles"]
    mock_streamlit.success.assert_called()
    mock_streamlit.rerun.assert_called()

def test_show_global_sidebar_upload_picture(mock_streamlit):
    """Test uploading a profile picture."""
    mock_streamlit.session_state.clear()
    mock_streamlit.session_state.update({
        "profiles": ["Default Family"],
        "active_profile": "Default Family",
        "profile_pictures": {},
        "gemini_api_key": ""
    })
    mock_streamlit.secrets = {}

    # Prevent adding new member
    mock_streamlit.button.return_value = False

    # Ensure active profile remains "Default Family"
    mock_streamlit.sidebar.selectbox.return_value = "Default Family"

    # Mock file uploader
    uploaded_file = MagicMock()
    uploaded_file.getvalue.return_value = b"image_data"
    mock_streamlit.sidebar.file_uploader.return_value = uploaded_file

    utils.show_global_sidebar()

    assert "Default Family" in mock_streamlit.session_state["profile_pictures"]
    assert mock_streamlit.session_state["profile_pictures"]["Default Family"] == b"image_data"

def test_show_global_sidebar_api_key_update(mock_streamlit):
    """Test updating API key via sidebar."""
    mock_streamlit.session_state.clear()
    mock_streamlit.session_state.update({
        "profiles": ["Default Family"],
        "active_profile": "Default Family",
        "profile_pictures": {},
        "gemini_api_key": "old_key"
    })
    mock_streamlit.secrets = {}

    mock_streamlit.button.return_value = False
    mock_streamlit.sidebar.selectbox.return_value = "Default Family"
    mock_streamlit.sidebar.file_uploader.return_value = None

    # Mock text input for API key (second text_input call)
    mock_streamlit.sidebar.text_input.return_value = "new_key"

    utils.show_global_sidebar()

    assert mock_streamlit.session_state["gemini_api_key"] == "new_key"
    mock_streamlit.rerun.assert_called()

# --- get_db_connection Tests ---

def test_get_db_connection_success_nested(mock_streamlit, mock_gspread):
    """Test successful connection with nested secrets."""
    mock_streamlit.secrets = {
        "gcp_service_account": {"project_id": "test", "private_key": "key"}
    }

    # Mock gspread return values
    gc = MagicMock()
    sh = MagicMock()
    worksheet = MagicMock()

    mock_gspread.service_account_from_dict.return_value = gc
    gc.open.return_value = sh
    sh.sheet1 = worksheet

    result = utils.get_db_connection()

    assert result == worksheet
    mock_gspread.service_account_from_dict.assert_called_with({"project_id": "test", "private_key": "key"})
    gc.open.assert_called_with("PIEZA_DB")

def test_get_db_connection_success_flat(mock_streamlit, mock_gspread):
    """Test successful connection with flat secrets."""
    mock_streamlit.secrets = {
        "project_id": "test", "private_key": "key"
    }

    # Mock gspread
    gc = MagicMock()
    sh = MagicMock()
    worksheet = MagicMock()

    mock_gspread.service_account_from_dict.return_value = gc
    gc.open.return_value = sh
    sh.sheet1 = worksheet

    result = utils.get_db_connection()

    assert result == worksheet
    # Expect all secrets passed because of dict(st.secrets)
    mock_gspread.service_account_from_dict.assert_called()

def test_get_db_connection_missing_secrets(mock_streamlit, mock_gspread):
    """Test handling of missing secrets."""
    mock_streamlit.secrets = {}

    result = utils.get_db_connection()

    assert result is None
    mock_streamlit.error.assert_called_with("Missing Google Cloud credentials in Streamlit secrets!")

def test_get_db_connection_sheet_not_found(mock_streamlit, mock_gspread):
    """Test handling of SpreadsheetNotFound exception."""
    mock_streamlit.secrets = {
        "gcp_service_account": {"project_id": "test"}
    }

    gc = MagicMock()
    mock_gspread.service_account_from_dict.return_value = gc

    # Create a real exception class for SpreadsheetNotFound to attach to the mock
    class SpreadsheetNotFound(Exception):
        pass
    mock_gspread.exceptions.SpreadsheetNotFound = SpreadsheetNotFound

    gc.open.side_effect = SpreadsheetNotFound()

    result = utils.get_db_connection()

    assert result is None
    mock_streamlit.error.assert_called()
    assert "Google Sheet 'PIEZA_DB' not found" in mock_streamlit.error.call_args[0][0]

# --- fetch_transactions Tests ---

def test_fetch_transactions_success(mock_streamlit):
    """Test fetching transactions successfully."""
    # Mock get_db_connection
    worksheet = MagicMock()
    worksheet.get_all_records.return_value = [
        {"ID": "1", "Amount": 100},
        {"ID": "2", "Amount": 200}
    ]

    with patch("utils.get_db_connection", return_value=worksheet):
        df = utils.fetch_transactions()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert df.iloc[0]["Amount"] == 100

def test_fetch_transactions_empty(mock_streamlit):
    """Test fetching transactions when sheet is empty."""
    worksheet = MagicMock()
    worksheet.get_all_records.return_value = []

    with patch("utils.get_db_connection", return_value=worksheet):
        df = utils.fetch_transactions()

        assert isinstance(df, pd.DataFrame)
        assert df.empty

def test_fetch_transactions_connection_failed(mock_streamlit):
    """Test fetching transactions when connection fails."""
    with patch("utils.get_db_connection", return_value=None):
        df = utils.fetch_transactions()

        assert isinstance(df, pd.DataFrame)
        assert df.empty

# --- add_transaction Tests ---

def test_add_transaction_success(mock_streamlit):
    """Test adding a transaction successfully."""
    worksheet = MagicMock()

    with patch("utils.get_db_connection", return_value=worksheet):
        tx_data = {
            "ID": "123", "Profile": "Test", "Date": "2023-01-01",
            "Type": "Expense", "Category": "Food", "Amount": 50.0,
            "Bank Name": "Bank", "Has Proof": True
        }

        result = utils.add_transaction(tx_data)

        assert result is True
        worksheet.append_row.assert_called()
        # Verify arguments passed to append_row
        args = worksheet.append_row.call_args[0][0]
        assert args[0] == "123"
        assert args[5] == 50.0

def test_add_transaction_failure(mock_streamlit):
    """Test adding a transaction failure."""
    worksheet = MagicMock()
    worksheet.append_row.side_effect = Exception("API Error")

    with patch("utils.get_db_connection", return_value=worksheet):
        tx_data = {"ID": "123"}
        result = utils.add_transaction(tx_data)

        assert result is False
        mock_streamlit.error.assert_called()

# --- delete_transaction Tests ---

def test_delete_transaction_success(mock_streamlit):
    """Test deleting transactions successfully."""
    worksheet = MagicMock()
    # Mock existing records (rows 2, 3, 4)
    worksheet.get_all_records.return_value = [
        {"ID": "1"}, # Row 2
        {"ID": "2"}, # Row 3
        {"ID": "3"}  # Row 4
    ]

    with patch("utils.get_db_connection", return_value=worksheet):
        # Delete ID "1" and "3" (Rows 2 and 4)
        result = utils.delete_transaction(["1", "3"])

        assert result is True
        # Check that delete_row was called for row 4 then row 2 (descending order)
        calls = worksheet.delete_row.call_args_list
        assert len(calls) == 2
        # First call should be row 4 (ID 3)
        assert calls[0][0][0] == 4
        # Second call should be row 2 (ID 1)
        assert calls[1][0][0] == 2

def test_delete_transaction_failure(mock_streamlit):
    """Test deleting transactions failure."""
    worksheet = MagicMock()
    worksheet.get_all_records.side_effect = Exception("API Error")

    with patch("utils.get_db_connection", return_value=worksheet):
        result = utils.delete_transaction(["1"])

        assert result is False
        mock_streamlit.error.assert_called()
