import sys
import os
import unittest
from unittest.mock import MagicMock

# Mock streamlit and gspread before importing utils
# This is necessary because utils.py imports them at the top level
sys.modules['streamlit'] = MagicMock()
sys.modules['gspread'] = MagicMock()
sys.modules['pandas'] = MagicMock()

# Mock st.cache_resource as a pass-through decorator
def cache_resource(func):
    return func
sys.modules['streamlit'].cache_resource = cache_resource

# Add parent directory to path to allow importing utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from utils import get_bank_domain
except ImportError as e:
    print(f"Failed to import utils: {e}")
    sys.exit(1)

class TestSecurity(unittest.TestCase):
    def test_valid_domains(self):
        # Note: clean_name logic lowercases and removes spaces.
        # "Chase" -> "chase" -> override "chase.com" -> "https://logo.clearbit.com/chase.com"
        # "Bank of America" -> "bankofamerica" -> override "bankofamerica.com" -> "https://logo.clearbit.com/bankofamerica.com"
        # "Wells Fargo" -> "wellsfargo" -> override "wellsfargo.com" -> "https://logo.clearbit.com/wellsfargo.com"
        # "Normal Bank" -> "normalbank" -> "normalbank.com" -> "https://logo.clearbit.com/normalbank.com"

        valid_inputs = [
            ("Chase", "https://logo.clearbit.com/chase.com"),
            ("Bank of America", "https://logo.clearbit.com/bankofamerica.com"),
            ("Wells Fargo", "https://logo.clearbit.com/wellsfargo.com"),
            ("Normal Bank", "https://logo.clearbit.com/normalbank.com"),
        ]
        for name, expected in valid_inputs:
            with self.subTest(name=name):
                self.assertEqual(get_bank_domain(name), expected)

    def test_malicious_inputs(self):
        # These inputs would produce invalid domains or URLs if not sanitized/validated
        malicious_inputs = [
            ("evil.com/malicious", ""), # clean_name becomes "evil.com/malicious", invalid
            ("../etc/passwd", ""),      # clean_name becomes "../etc/passwd", invalid
            ("<script>alert(1)</script>", ""), # invalid chars
            ("bank with / inside", ""), # "bankwith/inside", invalid
            ("bank#hash", ""),          # "bank#hash", invalid
            ("bank?query=1", ""),       # "bank?query=1", invalid
            ("valid-bank", "https://logo.clearbit.com/valid-bank.com"), # clean_name "valid-bank", valid chars
        ]
        for name, expected in malicious_inputs:
            with self.subTest(name=name):
                self.assertEqual(get_bank_domain(name), expected, f"Failed for '{name}'")

    def test_empty_input(self):
        self.assertEqual(get_bank_domain(""), "")
        self.assertEqual(get_bank_domain(None), "")

if __name__ == '__main__':
    unittest.main()
