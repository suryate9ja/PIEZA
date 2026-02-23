import sys
from unittest.mock import MagicMock
import pytest

# Mock streamlit before any tests run
st_mock = MagicMock()

# Mock st.cache_resource as a simple decorator that just returns the function
def cache_resource(func):
    return func
st_mock.cache_resource = cache_resource

# Mock st.session_state to allow attribute access
class SessionState(dict):
    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(item)
    def __setattr__(self, key, value):
        self[key] = value

st_mock.session_state = SessionState()

# Mock st.secrets as a dict
st_mock.secrets = {}

# Mock st.sidebar
st_mock.sidebar = MagicMock()

# Mock st.warning and st.error
st_mock.warning = MagicMock()
st_mock.error = MagicMock()

# Assign the mock to sys.modules['streamlit']
sys.modules["streamlit"] = st_mock
