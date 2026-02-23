import pandas as pd
import numpy as np
import pytest
from utils import create_options_map

def test_create_options_map_standard():
    data = {
        "ID": ["1", "2"],
        "Date": ["2023-01-01", "2023-01-02"],
        "Category": ["Food", "Transport"],
        "Amount": [10.5, 20.0],
        "Type": ["Debit", "Credit"]
    }
    df = pd.DataFrame(data)
    expected = {
        "1": "2023-01-01 - Food - 10.5 (Debit)",
        "2": "2023-01-02 - Transport - 20.0 (Credit)"
    }
    assert create_options_map(df) == expected

def test_create_options_map_missing_columns():
    # Only ID provided
    data = {"ID": ["3"]}
    df = pd.DataFrame(data)
    # Expected behavior: missing columns are treated as empty strings
    # "Date" -> "", "Category" -> "", "Amount" -> "", "Type" -> ""
    # Format: "{Date} - {Category} - {Amount} ({Type})"
    # Result: " -  -  ()"
    expected = {"3": " -  -  ()"}
    assert create_options_map(df) == expected

def test_create_options_map_nans():
    # Test with NaN values
    data = {
        "ID": ["4"],
        "Date": ["2023-01-01"],
        "Category": [np.nan],
        "Amount": [100],
        "Type": ["Debit"]
    }
    df = pd.DataFrame(data)
    # NaN becomes 'nan' string
    expected = {"4": "2023-01-01 - nan - 100 (Debit)"}
    assert create_options_map(df) == expected

def test_create_options_map_none():
    # Test with None values
    data = {
        "ID": ["5"],
        "Date": ["2023-01-01"],
        "Category": [None],
        "Amount": [100],
        "Type": ["Debit"]
    }
    df = pd.DataFrame(data)
    # None becomes 'None' string
    expected = {"5": "2023-01-01 - None - 100 (Debit)"}
    assert create_options_map(df) == expected

def test_create_options_map_mixed_types():
    # Test with mixed types (int, float)
    data = {
        "ID": [6], # Int ID
        "Date": ["2023-01-01"],
        "Category": ["Food"],
        "Amount": [100], # Int amount
        "Type": ["Debit"]
    }
    df = pd.DataFrame(data)
    # ID converted to string "6"
    # Amount converted to string "100" (if int)
    expected = {"6": "2023-01-01 - Food - 100 (Debit)"}
    assert create_options_map(df) == expected

def test_create_options_map_empty():
    # Empty dataframe
    df = pd.DataFrame(columns=["ID", "Date", "Category", "Amount", "Type"])
    expected = {}
    assert create_options_map(df) == expected
