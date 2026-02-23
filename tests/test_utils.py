import sys
from unittest.mock import MagicMock
from typing import Optional, Dict, Any, List

# Mock gspread before import
gspread_mock = MagicMock()
sys.modules["gspread"] = gspread_mock

# Mock streamlit before import
st_mock = MagicMock()
# Mock st.cache_resource to be a decorator that returns the function
st_mock.cache_resource = lambda func: func
sys.modules["streamlit"] = st_mock

# Now import utils
import utils
import pandas as pd

def test_show_global_sidebar_signature():
    assert utils.show_global_sidebar.__annotations__["return"] is None

def test_get_db_connection_signature():
    # Check that return type hint exists
    assert "return" in utils.get_db_connection.__annotations__
    # The return type is Optional[gspread.Worksheet] which involves the mock
    # We can check str representation or just existence

def test_fetch_transactions_signature():
    assert "return" in utils.fetch_transactions.__annotations__
    assert utils.fetch_transactions.__annotations__["return"] is pd.DataFrame

def test_add_transaction_signature():
    assert "return" in utils.add_transaction.__annotations__
    assert utils.add_transaction.__annotations__["return"] is bool
    assert "tx_data" in utils.add_transaction.__annotations__
    # assert utils.add_transaction.__annotations__["tx_data"] == Dict[str, Any]
    # Equality check on typing constructs can be tricky depending on python version

def test_delete_transaction_signature():
    assert "return" in utils.delete_transaction.__annotations__
    assert utils.delete_transaction.__annotations__["return"] is bool
    assert "tx_ids_to_delete" in utils.delete_transaction.__annotations__
    # assert utils.delete_transaction.__annotations__["tx_ids_to_delete"] == List[str]
