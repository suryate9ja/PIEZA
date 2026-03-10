import streamlit as st
from utils import show_global_sidebar

st.set_page_config(
    page_title="PIEZA - Family Finance Tracker",
    page_icon="assets/logo.png" if __import__("os").path.exists("assets/logo.png") else None,
    layout="wide"
)

show_global_sidebar()

st.title("PIEZA")
st.subheader("Family Finance Tracker")

st.markdown("""
Use the sidebar navigation to move between pages:

- **Data Entry** — Add transactions manually or scan a bank screenshot with AI.
- **Transaction Ledger** — View, filter, and delete your recorded transactions.
- **AI Advisor** — Get personalised spending analysis and loan-clearing advice.

Configure your **Gemini API Key** in the sidebar settings to enable all AI features.
""")

st.info(f"Active Profile: {st.session_state.get('active_profile', 'Default Family')}")
