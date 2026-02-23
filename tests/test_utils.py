import pytest
from unittest.mock import MagicMock, patch, call
import utils

def test_delete_transaction_happy_path():
    """Test successful deletion of transactions."""
    tx_ids = ["TX123", "TX125"]

    mock_worksheet = MagicMock()
    # Mock records. Row 1 is header.
    # idx 0 -> row 2: ID=TX123
    # idx 1 -> row 3: ID=TX124
    # idx 2 -> row 4: ID=TX125
    records = [
        {"ID": "TX123", "Amount": 100},
        {"ID": "TX124", "Amount": 200},
        {"ID": "TX125", "Amount": 300},
    ]
    mock_worksheet.get_all_records.return_value = records

    with patch("utils.get_db_connection", return_value=mock_worksheet):
        # Act
        result = utils.delete_transaction(tx_ids)

        # Assert
        assert result is True

        # Should delete row 4 then row 2 (descending order)
        calls = mock_worksheet.delete_row.call_args_list
        assert len(calls) == 2
        assert calls[0] == call(4)
        assert calls[1] == call(2)

def test_delete_transaction_not_found():
    """Test when transactions to delete are not found."""
    tx_ids = ["TX999"]
    mock_worksheet = MagicMock()
    records = [{"ID": "TX123"}]
    mock_worksheet.get_all_records.return_value = records

    with patch("utils.get_db_connection", return_value=mock_worksheet):
        result = utils.delete_transaction(tx_ids)
        assert result is True
        mock_worksheet.delete_row.assert_not_called()

def test_delete_transaction_connection_fail():
    """Test when get_db_connection returns None."""
    with patch("utils.get_db_connection", return_value=None):
        result = utils.delete_transaction(["TX123"])
        assert result is False

def test_delete_transaction_exception(mock_streamlit):
    """Test exception handling during deletion."""
    mock_worksheet = MagicMock()
    mock_worksheet.get_all_records.side_effect = Exception("API Error")

    # We verify st.error is called
    mock_st_error = mock_streamlit.error

    with patch("utils.get_db_connection", return_value=mock_worksheet):
        result = utils.delete_transaction(["TX123"])

        assert result is False
        mock_st_error.assert_called_once()
        args, _ = mock_st_error.call_args
        assert "API Error" in args[0]
