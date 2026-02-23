import sys
import pytest
from unittest.mock import MagicMock

# Define a dict subclass that supports attribute access
class MockSessionState(dict):
    """A dictionary that also allows attribute access."""
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

# Create a global mock for streamlit
# This must be done at the top level of conftest.py
st_mock = MagicMock()

# Mock st.cache_resource immediately
def cache_resource_mock(func):
    return func
st_mock.cache_resource = cache_resource_mock

# Mock st.secrets
st_mock.secrets = {}

# Mock st.session_state using our custom class
st_mock.session_state = MockSessionState()

# Patch sys.modules
sys.modules["streamlit"] = st_mock

@pytest.fixture
def mock_streamlit():
    """
    Fixture to provide a clean streamlit mock for each test.
    It resets the global mock's state and re-applies necessary attributes.
    """
    st_mock.reset_mock()
    # Re-initialize session_state with our custom class
    st_mock.session_state = MockSessionState()
    st_mock.secrets = {}
    st_mock.cache_resource = cache_resource_mock

    # Mock sidebar as a MagicMock so we can check calls on it
    st_mock.sidebar = MagicMock()

    # Also need to ensure st.text_input, st.button etc are mocks
    # MagicMock automatically creates them on access, but reset_mock might clear side effects

    return st_mock

@pytest.fixture
def mock_gspread(mocker):
    """
    Fixture to mock the gspread module used in utils.py.
    """
    return mocker.patch("utils.gspread")
