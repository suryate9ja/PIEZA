import streamlit as st
import os
import logging
from typing import Optional, Dict, Any, List
import re
import gspread
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def show_global_sidebar() -> None:
    st.sidebar.title("PIEZA Settings")

    if 'profiles' not in st.session_state:
        st.session_state.profiles = ["Default Family"]
    if 'active_profile' not in st.session_state:
        st.session_state.active_profile = st.session_state.profiles[0]
    if 'profile_pictures' not in st.session_state:
        st.session_state.profile_pictures = {}
    if 'gemini_api_key' not in st.session_state:
        st.session_state.gemini_api_key = st.secrets.get("gemini_api_key", "")

    st.sidebar.header("User Profile")

    selected_profile = st.sidebar.selectbox(
        "Select Family Member",
        st.session_state.profiles,
        index=st.session_state.profiles.index(st.session_state.active_profile)
    )
    st.session_state.active_profile = selected_profile

    with st.sidebar.expander("Add New Member"):
        new_member = st.text_input("Name")
        if st.button("Add"):
            if new_member and new_member not in st.session_state.profiles:
                st.session_state.profiles.append(new_member)
                st.success(f"Added {new_member}!")
                st.rerun()
            elif new_member in st.session_state.profiles:
                st.warning("Member already exists.")

    st.sidebar.subheader("Profile Picture")
    uploaded_pic = st.sidebar.file_uploader("Upload Picture", type=["png", "jpg", "jpeg"])

    if uploaded_pic is not None:
        st.session_state.profile_pictures[st.session_state.active_profile] = uploaded_pic.getvalue()

    if st.session_state.active_profile in st.session_state.profile_pictures:
        st.sidebar.image(
            st.session_state.profile_pictures[st.session_state.active_profile],
            caption=f"{st.session_state.active_profile}'s Picture",
            width=150
        )
    else:
        st.sidebar.info("No profile picture set.")

    st.sidebar.markdown("---")

    st.sidebar.header("AI Integrations")
    api_key = st.sidebar.text_input(
        "Gemini API Key",
        value=st.session_state.gemini_api_key,
        type="password",
        help="Required for OCR and AI Advisor features."
    )
    if api_key != st.session_state.gemini_api_key:
        st.session_state.gemini_api_key = api_key
        st.rerun()

    if not st.session_state.gemini_api_key:
        st.sidebar.warning("API Key missing. AI features will be disabled.")
    else:
        st.sidebar.success("API Key configured.")


# ── Google Sheets helpers ──────────────────────────────────────────────────────

@st.cache_resource
def get_db_connection() -> Optional[gspread.Worksheet]:
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
        elif "project_id" in st.secrets and "private_key" in st.secrets:
            creds_dict = dict(st.secrets)
        else:
            st.error("Missing Google Cloud credentials in Streamlit secrets. "
                     "Add a [gcp_service_account] section to your secrets.toml.")
            return None

        gc = gspread.service_account_from_dict(creds_dict)
        sh = gc.open("PIEZA_DB")
        return sh.sheet1

    except gspread.exceptions.SpreadsheetNotFound:
        st.error(
            "Google Sheet 'PIEZA_DB' not found. "
            "Create a sheet with that exact name and share it with your service account email."
        )
        return None
    except Exception as e:
        logger.error(f"Error connecting to Google Sheets: {e}", exc_info=True)
        st.error(f"Could not connect to Google Sheets: {e}")
        return None


def fetch_transactions() -> pd.DataFrame:
    worksheet = get_db_connection()
    if worksheet is None:
        return pd.DataFrame()
    try:
        records = worksheet.get_all_records()
        if not records:
            return pd.DataFrame()
        return pd.DataFrame(records)
    except Exception as e:
        st.warning(
            "Could not fetch records. "
            "Ensure Row 1 of PIEZA_DB has these headers: "
            "ID | Profile | Date | Type | Category | Amount | Bank Name | Has Proof"
        )
        logger.error(f"fetch_transactions error: {e}", exc_info=True)
        return pd.DataFrame()


def add_transaction(tx_data: Dict[str, Any]) -> bool:
    worksheet = get_db_connection()
    if worksheet is None:
        return False
    try:
        row = [
            str(tx_data.get("ID", "")),
            str(tx_data.get("Profile", "")),
            str(tx_data.get("Date", "")),
            str(tx_data.get("Type", "")),
            str(tx_data.get("Category", "")),
            float(tx_data.get("Amount", 0.0)),
            str(tx_data.get("Bank Name", "")),
            str(tx_data.get("Has Proof", False)),
        ]
        worksheet.append_row(row)
        return True
    except Exception as e:
        logger.error(f"Error saving to Google Sheets: {e}", exc_info=True)
        st.error(f"Could not save transaction: {e}")
        return False


def delete_transaction(tx_ids_to_delete: List[str]) -> bool:
    worksheet = get_db_connection()
    if worksheet is None:
        return False
    try:
        records = worksheet.get_all_records()
        rows_to_delete = [
            idx + 2  # +2: skip header row, convert 0-index to 1-index
            for idx, record in enumerate(records)
            if str(record.get("ID")) in tx_ids_to_delete
        ]
        rows_to_delete.sort(reverse=True)  # delete bottom-up to preserve indices
        for row_num in rows_to_delete:
            worksheet.delete_row(row_num)
        return True
    except Exception as e:
        logger.error(f"Error deleting from Google Sheets: {e}", exc_info=True)
        st.error(f"Could not delete transaction: {e}")
        return False


# ── Bank logo helper ───────────────────────────────────────────────────────────

_BANK_OVERRIDES = {
    "bankofamerica": "bankofamerica.com",
    "bofa": "bankofamerica.com",
    "chase": "chase.com",
    "wellsfargo": "wellsfargo.com",
    "citibank": "citi.com",
    "citi": "citi.com",
    "hdfc": "hdfcbank.com",
    "icici": "icicibank.com",
    "sbi": "onlinesbi.sbi",
    "axisbank": "axisbank.com",
    "axis": "axisbank.com",
    "kotak": "kotak.com",
    "americanexpress": "americanexpress.com",
    "amex": "americanexpress.com",
    "cred": "cred.club",
    "paytm": "paytm.com",
    "phonepe": "phonepe.com",
    "gpay": "pay.google.com",
    "googlepay": "pay.google.com",
}


def get_bank_domain(bank_name: str) -> str:
    """Returns a Clearbit logo URL for a given bank name, or empty string if unknown."""
    if not bank_name:
        return ""
    clean = str(bank_name).lower().replace(" ", "")
    domain = _BANK_OVERRIDES.get(clean, f"{clean}.com")
    if not re.match(r"^[a-z0-9.-]+$", domain):
        return ""
    return f"https://logo.clearbit.com/{domain}"


def create_options_map(df: pd.DataFrame) -> Dict[str, str]:
    """
    Creates a human-readable label for each transaction ID used in the
    delete multiselect on the Ledger page.
    Format: "YYYY-MM-DD | Category | Amount"
    """
    options = {}
    for _, row in df.iterrows():
        tx_id = str(row.get("ID", ""))
        date = str(row.get("Date", ""))
        category = str(row.get("Category", ""))
        amount = row.get("Amount", "")
        options[tx_id] = f"{date} | {category} | {amount}"
    return options
