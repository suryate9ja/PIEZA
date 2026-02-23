import pytest
import sys
from unittest.mock import MagicMock

# Mock streamlit before importing utils
sys.modules["streamlit"] = MagicMock()
# Mock other potential missing imports in utils.py
sys.modules["gspread"] = MagicMock()
sys.modules["oauth2client"] = MagicMock()
sys.modules["oauth2client.service_account"] = MagicMock()
sys.modules["pandas"] = MagicMock()

from datetime import datetime
from utils import parse_gemini_response

def test_parse_gemini_response_happy_path():
    response_text = '{"Date": "2023-10-27", "Amount": 123.45, "Bank Name": "Chase", "Type": "Expense"}'
    result = parse_gemini_response(response_text)

    assert result["Date"] == datetime(2023, 10, 27).date()
    assert result["Amount"] == 123.45
    assert result["Bank Name"] == "Chase"
    assert result["Type"] == "Expense"

def test_parse_gemini_response_with_markdown():
    response_text = '```json\n{"Date": "2023-10-27", "Amount": 123.45, "Bank Name": "Chase", "Type": "Expense"}\n```'
    result = parse_gemini_response(response_text)

    assert result["Date"] == datetime(2023, 10, 27).date()
    assert result["Amount"] == 123.45
    assert result["Bank Name"] == "Chase"
    assert result["Type"] == "Expense"

def test_parse_gemini_response_malformed_json():
    response_text = 'This is not JSON'
    result = parse_gemini_response(response_text)

    # Should return default values
    assert result["Date"] == datetime.today().date()
    assert result["Amount"] == 0.0
    assert result["Bank Name"] == ""
    assert result["Type"] == "Expense"

def test_parse_gemini_response_missing_fields():
    response_text = '{"Amount": 50.0}'
    result = parse_gemini_response(response_text)

    assert result["Date"] == datetime.today().date()
    assert result["Amount"] == 50.0
    assert result["Bank Name"] == ""
    assert result["Type"] == "Expense"

def test_parse_gemini_response_invalid_date():
    response_text = '{"Date": "invalid-date", "Amount": 50.0}'
    result = parse_gemini_response(response_text)

    assert result["Date"] == datetime.today().date()
    assert result["Amount"] == 50.0

def test_parse_gemini_response_invalid_amount():
    response_text = '{"Amount": "not-a-number"}'
    result = parse_gemini_response(response_text)

    assert result["Amount"] == 0.0
