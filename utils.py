import streamlit as st
import os
import logging
from typing import Optional, Dict, Any, List
import re
import gspread
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ── Design System ──────────────────────────────────────────────────────────────

def apply_custom_css() -> None:
    """Inject the premium Royal Green design system."""
    st.markdown(
        """
        <style>
        /* ═══════════════════════════════════════════════════════════
           PIEZA  ·  Premium Design System
           Palette: Royal Green · White · Grey
        ═══════════════════════════════════════════════════════════ */

        /* ── Font Stack ────────────────────────────────────────── */
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                         "Helvetica Neue", Arial, sans-serif;
            -webkit-font-smoothing: antialiased;
        }

        /* ── Page Background ───────────────────────────────────── */
        [data-testid="stAppViewContainer"] > .main {
            background-color: #F4F7F4;
        }
        .main .block-container {
            padding-top: 2.25rem;
            padding-bottom: 3rem;
            max-width: 1180px;
            animation: pageFadeIn 0.35s ease both;
        }
        @keyframes pageFadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to   { opacity: 1; transform: translateY(0);    }
        }

        /* ── Top accent bar ────────────────────────────────────── */
        [data-testid="stAppViewContainer"]::before {
            content: "";
            display: block;
            position: fixed;
            top: 0; left: 0; right: 0;
            height: 3px;
            background: linear-gradient(90deg, #1B5E20 0%, #4CAF50 60%, #1B5E20 100%);
            z-index: 9999;
        }

        /* ═══════════════════════════════════════════════════════
           SIDEBAR
        ══════════════════════════════════════════════════════ */
        [data-testid="stSidebar"] {
            background: linear-gradient(175deg, #14401C 0%, #1B5E20 45%, #245F28 100%);
            border-right: 1px solid #143D18;
        }
        [data-testid="stSidebar"] > div:first-child {
            background: transparent;
            padding-top: 1.75rem;
        }
        /* All sidebar text */
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] li,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] small,
        [data-testid="stSidebar"] div {
            color: #C8E6C9 !important;
        }
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #FFFFFF !important;
            font-weight: 700;
            letter-spacing: -0.2px;
        }
        /* Sidebar field labels */
        [data-testid="stSidebar"] .stSelectbox  > label,
        [data-testid="stSidebar"] .stTextInput  > label,
        [data-testid="stSidebar"] .stFileUploader > label {
            color: #A5D6A7 !important;
            font-size: 0.7rem !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.09em;
        }
        /* Sidebar inputs */
        [data-testid="stSidebar"] .stSelectbox > div > div,
        [data-testid="stSidebar"] .stTextInput  > div > div > input {
            background: rgba(255,255,255,0.08) !important;
            border: 1px solid rgba(255,255,255,0.18) !important;
            border-radius: 6px !important;
            color: #FFFFFF !important;
            transition: border-color 0.2s ease, background 0.2s ease;
        }
        [data-testid="stSidebar"] .stTextInput > div > div > input:focus {
            background: rgba(255,255,255,0.14) !important;
            border-color: rgba(255,255,255,0.45) !important;
        }
        /* Sidebar buttons */
        [data-testid="stSidebar"] .stButton > button {
            background: rgba(255,255,255,0.12) !important;
            color: #FFFFFF !important;
            border: 1px solid rgba(255,255,255,0.25) !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
            width: 100%;
            transition: background 0.2s ease, border-color 0.2s ease;
        }
        [data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(255,255,255,0.22) !important;
            border-color: rgba(255,255,255,0.45) !important;
        }
        /* Sidebar divider */
        [data-testid="stSidebar"] hr {
            border: none !important;
            border-top: 1px solid rgba(255,255,255,0.12) !important;
            margin: 1.25rem 0 !important;
        }
        /* Sidebar info / warning / success */
        [data-testid="stSidebar"] [data-testid="stAlert"] {
            background: rgba(255,255,255,0.08) !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            border-radius: 6px !important;
            color: #C8E6C9 !important;
            font-size: 0.8rem !important;
        }

        /* ═══════════════════════════════════════════════════════
           TYPOGRAPHY
        ══════════════════════════════════════════════════════ */
        h1 {
            font-size: 1.9rem !important;
            font-weight: 800 !important;
            color: #1B5E20 !important;
            letter-spacing: -0.4px;
            line-height: 1.2 !important;
            margin-bottom: 0.15rem !important;
        }
        h2 {
            font-size: 1.25rem !important;
            font-weight: 700 !important;
            color: #2E7D32 !important;
            letter-spacing: -0.2px;
        }
        h3 {
            font-size: 1rem !important;
            font-weight: 600 !important;
            color: #2E7D32 !important;
        }
        p, li {
            color: #3A3A3C;
            line-height: 1.65;
            font-size: 0.93rem;
        }
        .stMarkdown a {
            color: #388E3C;
            text-decoration: none;
            border-bottom: 1px solid #A5D6A7;
            transition: color 0.15s ease;
        }
        .stMarkdown a:hover { color: #1B5E20; }

        /* ── Section label (used above groups) ─────────────── */
        .section-label {
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #757575;
            margin-bottom: 0.6rem;
        }

        /* ═══════════════════════════════════════════════════════
           METRIC CARDS
        ══════════════════════════════════════════════════════ */
        [data-testid="metric-container"] {
            background: #FFFFFF;
            border: 1px solid #E8F5E9;
            border-left: 4px solid #4CAF50;
            border-radius: 10px;
            padding: 1.1rem 1.3rem;
            box-shadow: 0 1px 4px rgba(27,94,32,0.06), 0 4px 12px rgba(27,94,32,0.04);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        [data-testid="metric-container"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(27,94,32,0.12);
        }
        [data-testid="stMetricLabel"] > div {
            font-size: 0.68rem !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 0.09em;
            color: #757575 !important;
        }
        [data-testid="stMetricValue"] > div {
            font-size: 1.7rem !important;
            font-weight: 800 !important;
            color: #1B5E20 !important;
            letter-spacing: -0.5px;
        }
        [data-testid="stMetricDelta"] > div {
            font-size: 0.8rem !important;
            font-weight: 600 !important;
        }

        /* ═══════════════════════════════════════════════════════
           DATA FRAME
        ══════════════════════════════════════════════════════ */
        [data-testid="stDataFrame"] {
            background: #FFFFFF;
            border: 1px solid #E8F5E9;
            border-radius: 10px;
            box-shadow: 0 1px 4px rgba(27,94,32,0.06);
            overflow: hidden;
        }

        /* ═══════════════════════════════════════════════════════
           FORMS
        ══════════════════════════════════════════════════════ */
        [data-testid="stForm"] {
            background: #FFFFFF;
            border: 1px solid #E8F5E9;
            border-top: 3px solid #4CAF50;
            border-radius: 12px;
            padding: 1.75rem 2rem;
            box-shadow: 0 1px 4px rgba(27,94,32,0.06), 0 4px 14px rgba(27,94,32,0.04);
        }

        /* ── Input fields ──────────────────────────────────── */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {
            border-radius: 6px !important;
            border-color: #C8E6C9 !important;
            font-size: 0.93rem !important;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus {
            border-color: #4CAF50 !important;
            box-shadow: 0 0 0 3px rgba(76,175,80,0.14) !important;
        }
        .stSelectbox > div > div {
            border-radius: 6px !important;
            border-color: #C8E6C9 !important;
            font-size: 0.93rem !important;
            transition: border-color 0.2s ease;
        }
        .stSelectbox > div > div:focus-within {
            border-color: #4CAF50 !important;
            box-shadow: 0 0 0 3px rgba(76,175,80,0.14) !important;
        }
        /* Field labels */
        .stTextInput   > label,
        .stNumberInput > label,
        .stSelectbox   > label,
        .stDateInput   > label,
        .stFileUploader > label {
            font-size: 0.75rem !important;
            font-weight: 600 !important;
            color: #4A4A4A !important;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            margin-bottom: 0.3rem;
        }

        /* ═══════════════════════════════════════════════════════
           BUTTONS
        ══════════════════════════════════════════════════════ */
        /* Primary */
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #1B5E20 0%, #388E3C 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 7px !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
            letter-spacing: 0.4px;
            padding: 0.55rem 1.75rem !important;
            box-shadow: 0 2px 8px rgba(27,94,32,0.28) !important;
            transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.15s ease !important;
        }
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #2E7D32 0%, #43A047 100%) !important;
            box-shadow: 0 5px 18px rgba(27,94,32,0.38) !important;
            transform: translateY(-1px);
        }
        .stButton > button[kind="primary"]:active {
            transform: translateY(0);
            box-shadow: 0 2px 8px rgba(27,94,32,0.28) !important;
        }
        /* Secondary */
        .stButton > button[kind="secondary"],
        .stButton > button:not([kind]) {
            background: #FFFFFF !important;
            color: #2E7D32 !important;
            border: 1.5px solid #81C784 !important;
            border-radius: 7px !important;
            font-weight: 500 !important;
            font-size: 0.88rem !important;
            transition: background 0.2s ease, border-color 0.2s ease, transform 0.15s ease !important;
        }
        .stButton > button[kind="secondary"]:hover,
        .stButton > button:not([kind]):hover {
            background: #F1F8F2 !important;
            border-color: #4CAF50 !important;
            transform: translateY(-1px);
        }

        /* ═══════════════════════════════════════════════════════
           EXPANDERS
        ══════════════════════════════════════════════════════ */
        details[data-testid="stExpander"] {
            border: 1px solid #E8F5E9 !important;
            border-radius: 10px !important;
            overflow: hidden;
            background: #FFFFFF;
            box-shadow: 0 1px 4px rgba(27,94,32,0.05);
            transition: box-shadow 0.2s ease;
        }
        details[data-testid="stExpander"]:hover {
            box-shadow: 0 4px 12px rgba(27,94,32,0.09);
        }
        details[data-testid="stExpander"] summary {
            background: #FFFFFF;
            padding: 0.9rem 1.1rem;
            font-weight: 600;
            font-size: 0.9rem;
            color: #1B5E20;
            border-radius: 10px;
            transition: background 0.15s ease;
            cursor: pointer;
        }
        details[data-testid="stExpander"] summary:hover {
            background: #F1F8F2;
        }
        details[data-testid="stExpander"][open] summary {
            border-radius: 10px 10px 0 0;
            border-bottom: 1px solid #E8F5E9;
        }

        /* ═══════════════════════════════════════════════════════
           ALERTS
        ══════════════════════════════════════════════════════ */
        [data-testid="stAlert"] {
            border-radius: 8px !important;
            font-size: 0.88rem !important;
            border-left-width: 4px !important;
        }

        /* ═══════════════════════════════════════════════════════
           MISC
        ══════════════════════════════════════════════════════ */
        hr {
            border: none !important;
            border-top: 1px solid #E8F5E9 !important;
            margin: 1.75rem 0 !important;
        }
        .stCaption, [data-testid="stCaptionContainer"] {
            color: #757575 !important;
            font-size: 0.76rem !important;
        }
        /* Spinner color */
        .stSpinner > div {
            border-top-color: #4CAF50 !important;
        }
        /* Multiselect tags */
        [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
            background: #E8F5E9 !important;
            color: #1B5E20 !important;
            border: 1px solid #A5D6A7 !important;
            border-radius: 4px !important;
        }
        /* Checkbox */
        [data-testid="stCheckbox"] > label > div[data-testid="stCheckbox"] {
            border-color: #81C784 !important;
        }
        /* Tab underline accent */
        button[data-baseweb="tab"][aria-selected="true"] {
            border-bottom-color: #4CAF50 !important;
            color: #1B5E20 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Sidebar ────────────────────────────────────────────────────────────────────

def show_global_sidebar() -> None:
    # ── Brand mark ──
    st.sidebar.markdown(
        """
        <div style="padding: 0 0.5rem 0.25rem; border-bottom: 1px solid rgba(255,255,255,0.12); margin-bottom: 1rem;">
            <div style="font-size:1.45rem; font-weight:800; color:#FFFFFF; letter-spacing:-0.5px; line-height:1.1;">
                PIEZA
            </div>
            <div style="font-size:0.68rem; font-weight:600; color:#A5D6A7; text-transform:uppercase;
                        letter-spacing:0.12em; margin-top:2px;">
                Family Finance Tracker
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Session defaults ──
    if "profiles" not in st.session_state:
        st.session_state.profiles = ["Default Family"]
    if "active_profile" not in st.session_state:
        st.session_state.active_profile = st.session_state.profiles[0]
    if "profile_pictures" not in st.session_state:
        st.session_state.profile_pictures = {}
    if "gemini_api_key" not in st.session_state:
        st.session_state.gemini_api_key = st.secrets.get("gemini_api_key", "")

    # ── Profile section ──
    st.sidebar.markdown(
        '<p style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
        'letter-spacing:0.1em;color:#81C784;margin-bottom:0.5rem;">Profile</p>',
        unsafe_allow_html=True,
    )

    selected_profile = st.sidebar.selectbox(
        "Active member",
        st.session_state.profiles,
        index=st.session_state.profiles.index(st.session_state.active_profile),
        label_visibility="collapsed",
    )
    st.session_state.active_profile = selected_profile

    with st.sidebar.expander("Add new member"):
        new_member = st.text_input("Full name", placeholder="e.g. Priya")
        if st.button("Add member"):
            if new_member and new_member not in st.session_state.profiles:
                st.session_state.profiles.append(new_member)
                st.success(f"{new_member} added.")
                st.rerun()
            elif new_member in st.session_state.profiles:
                st.warning("That name already exists.")

    # Profile picture
    uploaded_pic = st.sidebar.file_uploader(
        "Profile picture", type=["png", "jpg", "jpeg"]
    )
    if uploaded_pic is not None:
        st.session_state.profile_pictures[
            st.session_state.active_profile
        ] = uploaded_pic.getvalue()

    if st.session_state.active_profile in st.session_state.profile_pictures:
        st.sidebar.image(
            st.session_state.profile_pictures[st.session_state.active_profile],
            caption=st.session_state.active_profile,
            width=120,
        )

    st.sidebar.markdown("---")

    # ── AI section ──
    st.sidebar.markdown(
        '<p style="font-size:0.65rem;font-weight:700;text-transform:uppercase;'
        'letter-spacing:0.1em;color:#81C784;margin-bottom:0.5rem;">AI Settings</p>',
        unsafe_allow_html=True,
    )
    api_key = st.sidebar.text_input(
        "Gemini API key",
        value=st.session_state.gemini_api_key,
        type="password",
        help="Required for the AI screenshot scanner and AI Advisor.",
        label_visibility="collapsed",
        placeholder="Paste your Gemini API key",
    )
    if api_key != st.session_state.gemini_api_key:
        st.session_state.gemini_api_key = api_key
        st.rerun()

    if not st.session_state.gemini_api_key:
        st.sidebar.warning("API key not set — AI features are disabled.")
    else:
        st.sidebar.success("API key active.")

    st.sidebar.markdown("---")

    # ── Active profile badge ──
    st.sidebar.markdown(
        f'<div style="text-align:center;padding:0.5rem 0;'
        f'font-size:0.78rem;color:#C8E6C9;">'
        f'Viewing as&nbsp;<strong style="color:#FFFFFF;">'
        f'{st.session_state.active_profile}</strong></div>',
        unsafe_allow_html=True,
    )


# ── Google Sheets helpers ──────────────────────────────────────────────────────

@st.cache_resource
def get_db_connection() -> Optional[gspread.Worksheet]:
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
        elif "project_id" in st.secrets and "private_key" in st.secrets:
            creds_dict = dict(st.secrets)
        else:
            st.error(
                "Google Cloud credentials are missing from Streamlit secrets. "
                "Add a [gcp_service_account] section to your secrets.toml."
            )
            return None

        gc = gspread.service_account_from_dict(creds_dict)
        sh = gc.open("PIEZA_DB")
        return sh.sheet1

    except gspread.exceptions.SpreadsheetNotFound:
        st.error(
            "Google Sheet 'PIEZA_DB' was not found. "
            "Create a sheet with that exact name and share it with your service account email."
        )
        return None
    except Exception as e:
        logger.error(f"Error connecting to Google Sheets: {e}", exc_info=True)
        st.error(
            "An unexpected error occurred while connecting to Google Sheets. "
            "Please check the logs."
        )
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
        st.error(
            "An error occurred while saving to Google Sheets. Please check the logs."
        )
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
        st.error(
            "An error occurred while deleting from Google Sheets. Please check the logs."
        )
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
    """Return a Clearbit logo URL for a given bank name, or an empty string if unknown."""
    if not bank_name:
        return ""
    clean = str(bank_name).lower().replace(" ", "")
    domain = _BANK_OVERRIDES.get(clean, f"{clean}.com")
    if not re.match(r"^[a-z0-9.-]+$", domain):
        return ""
    return f"https://logo.clearbit.com/{domain}"


def create_options_map(df: pd.DataFrame) -> Dict[str, str]:
    """
    Build a human-readable label for each transaction ID.
    Format: "YYYY-MM-DD  |  Category  |  Amount"
    Used in the delete multiselect on the Ledger page.
    """
    options = {}
    for _, row in df.iterrows():
        tx_id    = str(row.get("ID", ""))
        date     = str(row.get("Date", ""))
        category = str(row.get("Category", ""))
        amount   = row.get("Amount", "")
        options[tx_id] = f"{date}  |  {category}  |  {amount}"
    return options
