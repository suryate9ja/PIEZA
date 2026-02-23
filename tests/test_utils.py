import pytest
from utils import get_bank_domain

class TestGetBankDomain:
    def test_standard_bank_name(self):
        """Test that standard bank names are converted to .com domains."""
        assert get_bank_domain("Some Bank") == "https://logo.clearbit.com/somebank.com"
        assert get_bank_domain("My Credit Union") == "https://logo.clearbit.com/mycreditunion.com"

    def test_overrides(self):
        """Test known overrides."""
        overrides = {
            "Chase": "chase.com",
            "Bank of America": "bankofamerica.com",
            "BofA": "bankofamerica.com",
            "Wells Fargo": "wellsfargo.com",
            "Citi": "citi.com",
            "HDFC": "hdfcbank.com",
            "ICICI": "icicibank.com",
            "SBI": "onlinesbi.sbi",
            "Amex": "americanexpress.com",
            "American Express": "americanexpress.com"
        }
        for name, domain in overrides.items():
            expected = f"https://logo.clearbit.com/{domain}"
            assert get_bank_domain(name) == expected, f"Failed for {name}"

    def test_empty_input(self):
        """Test empty or None input."""
        assert get_bank_domain("") == ""
        assert get_bank_domain(None) == ""

    def test_whitespace_handling(self):
        """Test that whitespace is handled correctly."""
        assert get_bank_domain("  Chase  ") == "https://logo.clearbit.com/chase.com"
        assert get_bank_domain("Chase Bank") == "https://logo.clearbit.com/chasebank.com" # 'Chase Bank' is not in overrides, so it becomes chasebank.com unless caught by 'chase' override which it isn't (overrides are exact match on cleaned name)

    def test_mixed_case(self):
        """Test mixed case input."""
        assert get_bank_domain("cHaSe") == "https://logo.clearbit.com/chase.com"
