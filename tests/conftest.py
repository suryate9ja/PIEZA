import sys
import os
import pytest
from unittest.mock import MagicMock

# Add the project root to sys.path so we can import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Create the mock object once
mock_st = MagicMock()
mock_st.secrets = {}
mock_st.session_state = {}
mock_st.cache_resource = lambda func: func
mock_st.cache_data = lambda func: func

# Patch sys.modules immediately to intercept imports in test files
sys.modules["streamlit"] = mock_st

@pytest.fixture
def mock_streamlit():
    """Fixture to access the mocked streamlit module in tests."""
    return mock_st
