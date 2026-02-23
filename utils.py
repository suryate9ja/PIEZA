import streamlit as st
import os
import logging
from typing import Optional, Dict, Any, List
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def show_global_sidebar() -> None:
    """
    Renders the global sidebar used across all pages in the app.
    Handles user profiles, profile pictures, and the Gemini API key.
    """
    st.sidebar.title("PIEZA Settings")
    
    # Initialize session state variables if they don't exist
    if 'profiles' not in st.session_state:
        st.session_state.profiles = ["Default Family"]
    
    if 'active_profile' not in st.session_state:
        st.session_state.active_profile = st.session_state.profiles[0]
        
    if 'profile_pictures' not in st.session_state:
        st.session_state.profile_pictures = {}
        
    if 'gemini_api_key' not in st.session_state:
        # Check if the user has provided the API key in Streamlit Secrets
        st.session_state.gemini_api_key = st.secrets.get("gemini_api_key", "")

    # User Profiles Section
    st.sidebar.header("User Profile")
    
    # Select existing family member
    selected_profile = st.sidebar.selectbox(
        "Select Family Member", 
        st.session_state.profiles,
        index=st.session_state.profiles.index(st.session_state.active_profile)
    )
    st.session_state.active_profile = selected_profile
    
    # Add new family member
    with st.sidebar.expander("Add New Member"):
        new_member = st.text_input("Name")
        if st.button("Add"):
            if new_member and new_member not in st.session_state.profiles:
                st.session_state.profiles.append(new_member)
                st.success(f"Added {new_member}!")
                st.rerun()
            elif new_member in st.session_state.profiles:
                st.warning("Member already exists.")
                
    # Profile Picture Upload
    st.sidebar.subheader("Profile Picture")
    uploaded_pic = st.sidebar.file_uploader("Upload Picture", type=["png", "jpg", "jpeg"])
    
    if uploaded_pic is not None:
        # Save the uploaded file bytes to session state for the active profile
        st.session_state.profile_pictures[st.session_state.active_profile] = uploaded_pic.getvalue()
        
    # Display active profile picture if available
    if st.session_state.active_profile in st.session_state.profile_pictures:
        st.sidebar.image(
            st.session_state.profile_pictures[st.session_state.active_profile], 
            caption=f"{st.session_state.active_profile}'s Picture", 
            width=150
        )
    else:
        st.sidebar.info("No profile picture set.")
        
    st.sidebar.markdown("---")
    
    # API Key Section
    st.sidebar.header("AI Integrations")
    api_key = st.sidebar.text_input(
        "Gemini API Key", 
        value=st.session_state.gemini_api_key, 
        type="password",
        help="Required for OCR and AI Advisor features. Can also be set in Streamlit Secrets."
    )
    if api_key != st.session_state.gemini_api_key:
        st.session_state.gemini_api_key = api_key
        st.rerun()

    if not st.session_state.gemini_api_key:
        st.sidebar.warning("API Key missing. AI features will be disabled.")
    else:
        st.sidebar.success("API Key configured.")

# Database Functions using Google Sheets

@st.cache_resource
def get_db_connection() -> Optional[gspread.Worksheet]:
    """
    Connect to Google Sheets using credentials from st.secrets.
    Handles both nested [gcp_service_account] format and direct JSON structure.
    """
    try:
        # If user pasted the TOML format exactly, it's under the key "gcp_service_account"
        if "gcp_service_account" in st.secrets:
            # Convert Streamlit's AttrDict to a standard python dict for gspread
            creds_dict = dict(st.secrets["gcp_service_account"])
        # If user pasted the raw JSON file into the Streamlit secrets box directly
        elif "project_id" in st.secrets and "private_key" in st.secrets:
            # We copy the entire top-level secrets object into a standard dict
            creds_dict = dict(st.secrets)
        else:
            st.error("Missing Google Cloud credentials in Streamlit secrets!")
            return None
        
        # The new gspread way to auth from a dict
        gc = gspread.service_account_from_dict(creds_dict)
        # Connect to a default sheet name "PIEZA_DB"
        sh = gc.open("PIEZA_DB")
        worksheet = sh.sheet1
        return worksheet
    except gspread.exceptions.SpreadsheetNotFound:
        st.error("Google Sheet 'PIEZA_DB' not found. Please create it and share it with the service account email.")
        return None
    except Exception as e:
        logger.error(f"Error connecting to Google Sheets: {e}", exc_info=True)
        st.error("An unexpected error occurred while connecting to Google Sheets. Please check the logs.")
        return None

def fetch_transactions() -> pd.DataFrame:
    """Fetches all transactions from the Google Sheet and returns a DataFrame."""
    worksheet = get_db_connection()
    if worksheet is None:
        return pd.DataFrame()
        
    try:
        # Get all records as a list of dicts
        records = worksheet.get_all_records()
        if not records:
            return pd.DataFrame()
        return pd.DataFrame(records)
    except Exception as e:
        # If the sheet is completely empty and missing headers, get_all_records() fails
        st.warning("Could not fetch records. Please ensure row 1 has headers (ID, Profile, Date, Type, Category, Amount, Bank Name, Has Proof).")
        return pd.DataFrame()

def add_transaction(tx_data: Dict[str, Any]) -> bool:
    """Appends a new transaction row to the Google Sheet."""
    worksheet = get_db_connection()
    if worksheet is not None:
        try:
            # We assume order of headers in Google Sheet:
            # ID, Profile, Date, Type, Category, Amount, Bank Name, Has Proof
            
            # If the sheet is empty except for headers, we just append.
            # Convert values to strings or standard types for gspread
            row = [
                str(tx_data.get("ID", "")),
                str(tx_data.get("Profile", "")),
                str(tx_data.get("Date", "")),
                str(tx_data.get("Type", "")),
                str(tx_data.get("Category", "")),
                float(tx_data.get("Amount", 0.0)),
                str(tx_data.get("Bank Name", "")),
                str(tx_data.get("Has Proof", False))
            ]
            worksheet.append_row(row)
            return True
        except Exception as e:
            logger.error(f"Error saving to Google Sheets: {e}", exc_info=True)
            st.error("An error occurred while saving to Google Sheets. Please check the logs.")
            return False
    return False

def delete_transaction(tx_ids_to_delete: List[str]) -> bool:
    """Deletes transactions from the Google Sheet based on their IDs."""
    worksheet = get_db_connection()
    if worksheet is not None:
        try:
            records = worksheet.get_all_records()
            # Find the rows to delete. Note: Google Sheets rows are 1-indexed, 
            # and row 1 is usually headers. So record[0] is row 2.
            
            # We must delete from bottom to top to preserve row indices
            rows_to_delete = []
            for idx, record in enumerate(records):
                if str(record.get("ID")) in tx_ids_to_delete:
                    rows_to_delete.append(idx + 2) # +2 because index 0 is row 2 in the sheet
                    
            # Sort descending to delete from bottom up safely
            rows_to_delete.sort(reverse=True)
            
            for row_num in rows_to_delete:
                worksheet.delete_row(row_num)
                
            return True
        except Exception as e:
            logger.error(f"Error deleting from Google Sheets: {e}", exc_info=True)
            st.error("An error occurred while deleting from Google Sheets. Please check the logs.")
            return False
    return False

def get_bank_domain(bank_name):
    """
    Returns a secure URL for the bank logo using ClearBit.
    Validates the bank name to prevent URL injection.
    """
    if not bank_name:
        return ""

    # simple heuristic assuming domains like chase.com, bofa.com, etc.
    clean_name = str(bank_name).lower().replace(" ", "")

    # Add basic overrides for popular banks
    overrides = {
        "bankofamerica": "bankofamerica.com",
        "bofa": "bankofamerica.com",
        "chase": "chase.com",
        "wellsfargo": "wellsfargo.com",
        "citibank": "citi.com",
        "citi": "citi.com",
        "hdfc": "hdfcbank.com",
        "icici": "icicibank.com",
        "sbi": "onlinesbi.sbi",
        "americanexpress": "americanexpress.com",
        "amex": "americanexpress.com"
    }

    domain = overrides.get(clean_name, f"{clean_name}.com")

    # Security Validation: Ensure domain only contains safe characters
    # Allowed: alphanumeric, hyphen, dot
    if not re.match(r"^[a-z0-9.-]+$", domain):
        return "" # Return empty string or a default safe image URL if invalid

    return f"https://logo.clearbit.com/{domain}"
