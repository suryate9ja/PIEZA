import pytest
from unittest.mock import MagicMock
import sys
import os

# Add root directory to sys.path to ensure utils can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils

def test_add_transaction_success(mocker):
    """Test add_transaction successfully appends a row."""
    # Mock get_db_connection
    mock_worksheet = MagicMock()
    mock_get_db = mocker.patch('utils.get_db_connection', return_value=mock_worksheet)

    tx_data = {
        "ID": "123",
        "Profile": "TestProfile",
        "Date": "2023-10-27",
        "Type": "Expense",
        "Category": "Food",
        "Amount": 50.0,
        "Bank Name": "TestBank",
        "Has Proof": True
    }

    result = utils.add_transaction(tx_data)

    assert result is True

    expected_row = [
        "123", "TestProfile", "2023-10-27", "Expense", "Food", 50.0, "TestBank", "True"
    ]
    mock_worksheet.append_row.assert_called_once_with(expected_row)

def test_add_transaction_connection_failure(mocker):
    """Test add_transaction returns False when connection fails."""
    mocker.patch('utils.get_db_connection', return_value=None)

    tx_data = {"ID": "123"}
    result = utils.add_transaction(tx_data)

    assert result is False

def test_add_transaction_append_exception(mocker):
    """Test add_transaction returns False and logs error on append exception."""
    mock_worksheet = MagicMock()
    mock_worksheet.append_row.side_effect = Exception("API Error")
    mocker.patch('utils.get_db_connection', return_value=mock_worksheet)

    # Mock streamlit.error
    mock_st_error = mocker.patch('streamlit.error')

    tx_data = {"ID": "123"}
    result = utils.add_transaction(tx_data)

    assert result is False
    mock_st_error.assert_called_once()
    assert "Error saving to Google Sheets" in str(mock_st_error.call_args)

def test_add_transaction_defaults(mocker):
    """Test add_transaction uses default values for missing keys."""
    mock_worksheet = MagicMock()
    mocker.patch('utils.get_db_connection', return_value=mock_worksheet)

    # Empty dictionary
    tx_data = {}

    result = utils.add_transaction(tx_data)

    assert result is True

    # Defaults: ID="", Profile="", Date="", Type="", Category="", Amount=0.0, Bank Name="", Has Proof=False
    expected_row = [
        "", "", "", "", "", 0.0, "", "False"
    ]
    mock_worksheet.append_row.assert_called_once_with(expected_row)
