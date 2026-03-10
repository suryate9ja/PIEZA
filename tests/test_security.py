import sys
import os
import unittest

# Add parent directory to path to allow importing utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# conftest.py (loaded first by pytest) already patches sys.modules['streamlit']
# and imports utils. We just import the function under test directly.
from utils import get_bank_domain


class TestSecurity(unittest.TestCase):
    def test_valid_domains(self):
        # Note: clean_name logic lowercases and removes spaces.
        # "Chase" -> "chase" -> override "chase.com" -> "https://logo.clearbit.com/chase.com"
        # "Bank of America" -> "bankofamerica" -> override "bankofamerica.com"
        # "Wells Fargo" -> "wellsfargo" -> override "wellsfargo.com"
        # "Normal Bank" -> "normalbank" -> "normalbank.com"
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
        # These inputs would produce invalid domains or URLs if not sanitized.
        malicious_inputs = [
            ("evil.com/malicious", ""),           # "evil.com/malicious", invalid
            ("../etc/passwd", ""),                # "../etc/passwd", invalid
            ("<script>alert(1)</script>", ""),    # invalid chars
            ("bank with / inside", ""),           # "bankwith/inside", invalid
            ("bank#hash", ""),                    # "bank#hash", invalid
            ("bank?query=1", ""),                 # "bank?query=1", invalid
            ("valid-bank", "https://logo.clearbit.com/valid-bank.com"),  # valid chars
        ]
        for name, expected in malicious_inputs:
            with self.subTest(name=name):
                self.assertEqual(get_bank_domain(name), expected, f"Failed for '{name}'")

    def test_empty_input(self):
        self.assertEqual(get_bank_domain(""), "")
        self.assertEqual(get_bank_domain(None), "")


if __name__ == '__main__':
    unittest.main()
