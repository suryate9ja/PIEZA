import streamlit as st
from utils import show_global_sidebar

# Set page configuration for all pages
st.set_page_config(
    page_title="PIEZA - Family Finance Tracker", 
    layout="wide"
)

# Transactions will now be fetched from Google Sheets

# Show global sidebar
show_global_sidebar()

# Main Home Page Content
st.title("Welcome to PIEZA")
st.subheader("Your Family Finance Tracker")

st.markdown("""
Welcome to the multi-page version of PIEZA! 
Please select a page from the main sidebar navigation (on the left) to get started:

- **1 Data Entry**: Add new transactions manually or upload bank screenshots for auto-extraction.
- **2 Transaction Ledger**: View, manage, and delete your tracked transactions, and see your bank logos.
- **3 AI Advisor**: Get personalized spending reduction and loan-clearing advice from Gemini.

Make sure to configure your **Gemini API Key** in the global settings sidebar to enable the AI features.
""")

st.info(f"Active Profile: {st.session_state.active_profile}")
