import pandas as pd
from unittest.mock import MagicMock, patch
import pytest

# Ensure utils can be imported by making sure streamlit is mocked
# This is handled by conftest.py, but explicit import here triggers it
import utils

def test_fetch_transactions_no_connection():
    """Test fetch_transactions returns empty DataFrame when get_db_connection returns None."""
    with patch('utils.get_db_connection', return_value=None):
        df = utils.fetch_transactions()
        assert isinstance(df, pd.DataFrame)
        assert df.empty

def test_fetch_transactions_empty_records():
    """Test fetch_transactions returns empty DataFrame when worksheet is empty."""
    mock_worksheet = MagicMock()
    mock_worksheet.get_all_records.return_value = []

    with patch('utils.get_db_connection', return_value=mock_worksheet):
        df = utils.fetch_transactions()
        assert isinstance(df, pd.DataFrame)
        assert df.empty

def test_fetch_transactions_success():
    """Test fetch_transactions returns DataFrame with records."""
    mock_worksheet = MagicMock()
    records = [
        {"ID": "1", "Amount": 100},
        {"ID": "2", "Amount": 200}
    ]
    mock_worksheet.get_all_records.return_value = records

    with patch('utils.get_db_connection', return_value=mock_worksheet):
        df = utils.fetch_transactions()
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert len(df) == 2
        assert df.iloc[0]["ID"] == "1"

def test_fetch_transactions_exception():
    """Test fetch_transactions handles exceptions gracefully."""
    mock_worksheet = MagicMock()
    mock_worksheet.get_all_records.side_effect = Exception("API Error")

    with patch('utils.get_db_connection', return_value=mock_worksheet):
        # We patch streamlit.warning to verify it's called
        with patch('streamlit.warning') as mock_warning:
            df = utils.fetch_transactions()
            assert isinstance(df, pd.DataFrame)
            assert df.empty
            mock_warning.assert_called_once()
            args, _ = mock_warning.call_args
            assert "Could not fetch records" in args[0]
