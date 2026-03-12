import streamlit as st
import os
import logging
import calendar
from datetime import date
from typing import Optional, Dict, Any, List
import re
import gspread
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Sheet schemas ──────────────────────────────────────────────────────────────
_LOANS_HEADERS = [
    "ID", "Profile", "Loan Name", "Bank", "Principal",
    "Principal Left", "Interest Rate %", "Tenure Months", "EMI Day",
    "EMI Amount", "Start Date", "End Date", "Status",
]
_CARDS_HEADERS = [
    "ID", "Profile", "Card Name", "Bank",
    "Credit Limit", "Outstanding", "Min Payment", "Due Date", "Status",
]


# ── Design System ──────────────────────────────────────────────────────────────

def apply_custom_css() -> None:
    """Inject the PIEZA design system — creamy white, black text, royal green logo only."""
    st.markdown(
        """
        <style>
        /* ═══════════════════════════════════════════════════════════
           PIEZA  ·  Design System v2
           Background: Creamy White  ·  Text: Black  ·  Brand: Royal Green
        ═══════════════════════════════════════════════════════════ */

        /* ── Font Stack ────────────────────────────────────────── */
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI",
                         "Helvetica Neue", Arial, sans-serif;
            -webkit-font-smoothing: antialiased;
            color: #1A1A1A;
        }

        /* ── Page Background — Creamy White ────────────────────── */
        [data-testid="stAppViewContainer"],
        [data-testid="stAppViewContainer"] > .main {
            background-color: #FFFEF5 !important;
        }
        .main .block-container {
            padding-top: 4.75rem !important;
            padding-bottom: 3rem;
            max-width: 1180px;
            animation: pageFadeIn 0.35s ease both;
        }
        @keyframes pageFadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        /* ── Hide ALL Streamlit Chrome ─────────────────────────── */
        [data-testid="stHeader"]                  { display: none !important; }
        [data-testid="stSidebar"]                 { display: none !important; }
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        [data-testid="stSidebarNav"]              { display: none !important; }
        #MainMenu                                 { display: none !important; }
        footer                                    { display: none !important; }
        [data-testid="stToolbar"]                 { display: none !important; }
        [data-testid="stDecoration"]              { display: none !important; }

        /* ══════════════════════════════════════════════════════════
           CUSTOM FIXED NAVBAR
        ══════════════════════════════════════════════════════════ */
        .pz-navbar {
            position: fixed;
            top: 0; left: 0; right: 0;
            height: 56px;
            background: #FFFFFF;
            border-bottom: 1px solid #E8E8E8;
            z-index: 999999;
            display: flex;
            align-items: center;
            padding: 0 1.5rem;
            gap: 0.85rem;
            box-shadow: 0 1px 6px rgba(0,0,0,0.07);
        }
        .pz-nb-left {
            display: flex;
            align-items: center;
            gap: 0.7rem;
            position: relative;
        }
        /* PIEZA logo — ONLY this element uses royal green */
        .pz-logo {
            font-size: 1.35rem;
            font-weight: 800;
            color: #1B5E20 !important;
            letter-spacing: -0.5px;
            white-space: nowrap;
            margin-right: 0.2rem;
            user-select: none;
        }
        /* Profile selector pill */
        .pz-profile-selector {
            display: flex;
            align-items: center;
            gap: 0.38rem;
            cursor: pointer;
            padding: 0.26rem 0.6rem 0.26rem 0.38rem;
            border-radius: 20px;
            background: #F5F5F0;
            border: 1px solid #E0E0E0;
            user-select: none;
            white-space: nowrap;
            transition: background 0.15s, border-color 0.15s;
        }
        .pz-profile-selector:hover {
            background: #EBF5EB;
            border-color: #A5D6A7;
        }
        .pz-ps-avatar {
            width: 22px; height: 22px;
            border-radius: 50%;
            background: #1B5E20;
            color: white;
            display: flex; align-items: center; justify-content: center;
            font-size: 0.68rem; font-weight: 700;
            flex-shrink: 0;
        }
        .pz-ps-name {
            font-size: 0.83rem;
            color: #1A1A1A;
            font-weight: 500;
            max-width: 120px;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .pz-ps-arrow { font-size: 0.58rem; color: #888; }

        /* ── Profile dropdown panel ────────────────────────── */
        .pz-profile-dropdown {
            position: absolute;
            top: calc(100% + 9px);
            left: 0;
            background: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.13);
            min-width: 230px;
            z-index: 1000001;
            display: none;
            overflow: hidden;
            padding: 0.35rem 0;
        }
        .pz-profile-dropdown.pz-dd-open { display: block; }
        .pz-profile-item {
            display: flex;
            align-items: center;
            padding: 0.52rem 0.9rem;
            cursor: pointer;
            transition: background 0.1s;
        }
        .pz-profile-item:hover { background: #F5F5F0; }
        .pz-profile-item.pz-profile-active { background: #EBF5EB; }
        .pz-pi-avatar {
            width: 30px; height: 30px;
            border-radius: 50%;
            background: #1B5E20;
            color: white;
            display: flex; align-items: center; justify-content: center;
            font-size: 0.78rem; font-weight: 700;
            margin-right: 0.65rem; flex-shrink: 0;
        }
        .pz-pi-name { flex: 1; font-size: 0.88rem; color: #1A1A1A; }
        .pz-pi-edit {
            visibility: hidden;
            font-size: 0.82rem;
            color: #888;
            padding: 0.18rem 0.32rem;
            border-radius: 4px;
            transition: background 0.1s, color 0.1s;
            cursor: pointer;
        }
        .pz-profile-item:hover .pz-pi-edit { visibility: visible; }
        .pz-pi-edit:hover { background: #E0E0E0; color: #1A1A1A; }
        .pz-pi-add {
            display: flex;
            align-items: center;
            padding: 0.52rem 0.9rem;
            color: #1B5E20;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            border-top: 1px solid #F0F0F0;
            margin-top: 0.25rem;
            transition: background 0.1s;
        }
        .pz-pi-add:hover { background: #F5F5F0; }

        /* ── Navbar page links ─────────────────────────────── */
        .pz-nb-nav {
            display: flex;
            align-items: center;
            gap: 0.1rem;
            flex: 1;
        }
        .pz-nav-link {
            padding: 0.3rem 0.68rem;
            border-radius: 6px;
            font-size: 0.86rem;
            color: #1A1A1A;
            text-decoration: none !important;
            font-weight: 500;
            transition: background 0.15s, color 0.15s;
            white-space: nowrap;
        }
        .pz-nav-link:hover {
            background: #EBF5EB;
            color: #1B5E20;
        }
        .pz-nav-link.pz-nav-active {
            background: #EBF5EB;
            color: #1B5E20;
            font-weight: 600;
        }

        /* ── Profile avatar (top right) ────────────────────── */
        .pz-nb-right { margin-left: auto; display: flex; align-items: center; }
        .pz-avatar-container { position: relative; }
        .pz-avatar-btn {
            width: 34px; height: 34px;
            border-radius: 50%;
            background: #1B5E20;
            color: white;
            display: flex; align-items: center; justify-content: center;
            font-size: 0.88rem; font-weight: 700;
            cursor: pointer;
            border: none;
            transition: background 0.15s, box-shadow 0.15s;
            flex-shrink: 0;
            user-select: none;
        }
        .pz-avatar-btn:hover {
            background: #2E7D32;
            box-shadow: 0 2px 8px rgba(27,94,32,0.32);
        }
        /* Profile popup (top-right) */
        .pz-profile-popup {
            position: absolute;
            top: calc(100% + 10px);
            right: 0;
            background: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.13);
            min-width: 190px;
            padding: 1rem 1rem 0.75rem;
            z-index: 1000002;
            display: none;
            text-align: center;
        }
        .pz-profile-popup.pz-pp-open { display: block; }
        .pz-pp-avatar {
            width: 48px; height: 48px;
            border-radius: 50%;
            background: #1B5E20;
            color: white;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.2rem; font-weight: 700;
            margin: 0 auto 0.5rem;
        }
        .pz-pp-name {
            font-size: 0.9rem; font-weight: 600;
            color: #1A1A1A; margin-bottom: 0.75rem;
        }
        .pz-pp-divider { height: 1px; background: #F0F0F0; margin-bottom: 0.6rem; }
        .pz-pp-link {
            display: block;
            color: #1B5E20;
            font-size: 0.84rem;
            font-weight: 500;
            text-decoration: none !important;
            padding: 0.32rem 0.5rem;
            border-radius: 6px;
            transition: background 0.1s;
        }
        .pz-pp-link:hover { background: #EBF5EB; }

        /* ── Add-profile inline form ───────────────────────── */
        .pz-add-profile-bar {
            background: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 10px;
            padding: 0.85rem 1.2rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.05);
            animation: pageFadeIn 0.2s ease both;
        }

        /* ══════════════════════════════════════════════════════════
           TYPOGRAPHY — ALL BLACK, only .pz-logo stays green
        ══════════════════════════════════════════════════════════ */
        h1 {
            font-size: 1.9rem !important;
            font-weight: 800 !important;
            color: #1A1A1A !important;
            letter-spacing: -0.4px;
            line-height: 1.2 !important;
            margin-bottom: 0.15rem !important;
        }
        h2 {
            font-size: 1.25rem !important;
            font-weight: 700 !important;
            color: #1A1A1A !important;
            letter-spacing: -0.2px;
        }
        h3 {
            font-size: 1rem !important;
            font-weight: 600 !important;
            color: #1A1A1A !important;
        }
        p, li { color: #1A1A1A; line-height: 1.65; font-size: 0.93rem; }
        .stMarkdown a {
            color: #1B5E20;
            text-decoration: none;
            border-bottom: 1px solid #A5D6A7;
            transition: color 0.15s;
        }
        .stMarkdown a:hover { color: #2E7D32; }
        .section-label {
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #757575;
            margin-bottom: 0.6rem;
        }

        /* ══════════════════════════════════════════════════════════
           METRIC CARDS
        ══════════════════════════════════════════════════════════ */
        [data-testid="metric-container"] {
            background: #FFFFFF;
            border: 1px solid #E8E8E8;
            border-left: 4px solid #4CAF50;
            border-radius: 10px;
            padding: 1.1rem 1.3rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.05), 0 4px 12px rgba(0,0,0,0.03);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        [data-testid="metric-container"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.09);
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
            color: #1A1A1A !important;
            letter-spacing: -0.5px;
        }
        [data-testid="stMetricDelta"] > div {
            font-size: 0.8rem !important;
            font-weight: 600 !important;
        }

        /* ══════════════════════════════════════════════════════════
           DATA FRAME
        ══════════════════════════════════════════════════════════ */
        [data-testid="stDataFrame"] {
            background: #FFFFFF;
            border: 1px solid #E8E8E8;
            border-radius: 10px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.05);
            overflow: hidden;
        }

        /* ══════════════════════════════════════════════════════════
           FORMS
        ══════════════════════════════════════════════════════════ */
        [data-testid="stForm"] {
            background: #FFFFFF;
            border: 1px solid #E8E8E8;
            border-top: 3px solid #4CAF50;
            border-radius: 12px;
            padding: 1.75rem 2rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.05), 0 4px 14px rgba(0,0,0,0.03);
        }
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {
            border-radius: 6px !important;
            border-color: #D8D8D8 !important;
            font-size: 0.93rem !important;
            color: #1A1A1A !important;
            background: #FFFFFF !important;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus {
            border-color: #4CAF50 !important;
            box-shadow: 0 0 0 3px rgba(76,175,80,0.14) !important;
        }
        .stSelectbox > div > div {
            border-radius: 6px !important;
            border-color: #D8D8D8 !important;
            font-size: 0.93rem !important;
            color: #1A1A1A !important;
            background: #FFFFFF !important;
            transition: border-color 0.2s;
        }
        .stSelectbox > div > div:focus-within {
            border-color: #4CAF50 !important;
            box-shadow: 0 0 0 3px rgba(76,175,80,0.14) !important;
        }
        .stTextInput > label, .stNumberInput > label,
        .stSelectbox > label, .stDateInput > label,
        .stFileUploader > label {
            font-size: 0.75rem !important;
            font-weight: 600 !important;
            color: #4A4A4A !important;
            text-transform: uppercase;
            letter-spacing: 0.07em;
            margin-bottom: 0.3rem;
        }

        /* ══════════════════════════════════════════════════════════
           BUTTONS
        ══════════════════════════════════════════════════════════ */
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
            transition: background 0.2s, box-shadow 0.2s, transform 0.15s !important;
        }
        .stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #2E7D32 0%, #43A047 100%) !important;
            box-shadow: 0 5px 18px rgba(27,94,32,0.38) !important;
            transform: translateY(-1px);
        }
        .stButton > button[kind="primary"]:active { transform: translateY(0); }
        .stButton > button[kind="secondary"],
        .stButton > button:not([kind]) {
            background: #FFFFFF !important;
            color: #1A1A1A !important;
            border: 1.5px solid #D8D8D8 !important;
            border-radius: 7px !important;
            font-weight: 500 !important;
            font-size: 0.88rem !important;
            transition: background 0.2s, border-color 0.2s, transform 0.15s !important;
        }
        .stButton > button[kind="secondary"]:hover,
        .stButton > button:not([kind]):hover {
            background: #F5F5F0 !important;
            border-color: #A5D6A7 !important;
            transform: translateY(-1px);
        }

        /* ══════════════════════════════════════════════════════════
           EXPANDERS
        ══════════════════════════════════════════════════════════ */
        details[data-testid="stExpander"] {
            border: 1px solid #E8E8E8 !important;
            border-radius: 10px !important;
            overflow: hidden;
            background: #FFFFFF;
            box-shadow: 0 1px 4px rgba(0,0,0,0.04);
            transition: box-shadow 0.2s;
        }
        details[data-testid="stExpander"]:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        details[data-testid="stExpander"] summary {
            background: #FFFFFF;
            padding: 0.9rem 1.1rem;
            font-weight: 600;
            font-size: 0.9rem;
            color: #1A1A1A;
            border-radius: 10px;
            transition: background 0.15s;
            cursor: pointer;
        }
        details[data-testid="stExpander"] summary:hover { background: #F5F5F0; }
        details[data-testid="stExpander"][open] summary {
            border-radius: 10px 10px 0 0;
            border-bottom: 1px solid #E8E8E8;
        }

        /* ══════════════════════════════════════════════════════════
           ALERTS
        ══════════════════════════════════════════════════════════ */
        [data-testid="stAlert"] {
            border-radius: 8px !important;
            font-size: 0.88rem !important;
            border-left-width: 4px !important;
        }

        /* ══════════════════════════════════════════════════════════
           MISC
        ══════════════════════════════════════════════════════════ */
        hr {
            border: none !important;
            border-top: 1px solid #E8E8E8 !important;
            margin: 1.75rem 0 !important;
        }
        .stCaption, [data-testid="stCaptionContainer"] {
            color: #757575 !important;
            font-size: 0.76rem !important;
        }
        .stSpinner > div { border-top-color: #4CAF50 !important; }
        [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
            background: #EBF5EB !important;
            color: #1B5E20 !important;
            border: 1px solid #A5D6A7 !important;
            border-radius: 4px !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            border-bottom-color: #4CAF50 !important;
            color: #1B5E20 !important;
        }

        /* ══════════════════════════════════════════════════════════
           EXPANDABLE SEARCH BAR (Transaction Ledger)
        ══════════════════════════════════════════════════════════ */
        .pz-search-outer {
            display: flex;
            justify-content: center;
            margin: 0.75rem 0 1.25rem;
        }

        /* ══════════════════════════════════════════════════════════
           PAGINATION
        ══════════════════════════════════════════════════════════ */
        .pz-pagination {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.35rem;
            margin: 1.25rem 0 0.5rem;
            flex-wrap: wrap;
        }
        .pz-page-btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 34px; height: 34px;
            border-radius: 7px;
            font-size: 0.85rem;
            font-weight: 500;
            cursor: pointer;
            border: 1.5px solid #E0E0E0;
            background: #FFFFFF;
            color: #1A1A1A;
            transition: background 0.15s, border-color 0.15s, color 0.15s;
            user-select: none;
            padding: 0 0.5rem;
        }
        .pz-page-btn:hover {
            background: #EBF5EB;
            border-color: #A5D6A7;
            color: #1B5E20;
        }
        .pz-page-btn.pz-page-active {
            background: #1B5E20;
            border-color: #1B5E20;
            color: #FFFFFF;
            font-weight: 700;
        }
        .pz-page-btn.pz-page-disabled {
            opacity: 0.38;
            cursor: not-allowed;
            pointer-events: none;
        }
        .pz-page-ellipsis {
            font-size: 0.85rem;
            color: #888;
            padding: 0 0.2rem;
            user-select: none;
        }
        .pz-page-info {
            text-align: center;
            font-size: 0.78rem;
            color: #757575;
            margin-top: 0.25rem;
        }

        /* ══════════════════════════════════════════════════════════
           HOVER BUTTON  (ported from HoverButton React component)
           Glass-morphism pill with pointer-following glow circles
        ══════════════════════════════════════════════════════════ */
        .pz-hover-btn {
            position: relative;
            isolation: isolate;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0.72rem 2rem;
            border-radius: 2rem;
            font-family: inherit;
            font-size: 0.95rem;
            font-weight: 600;
            line-height: 1.5;
            color: #1B5E20;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            background: rgba(27, 94, 32, 0.07);
            cursor: pointer;
            overflow: hidden;
            border: none;
            outline: none;
            text-decoration: none !important;
            box-shadow:
                inset 0 0 0 1px rgba(27, 94, 32, 0.22),
                inset 0 0 16px 0  rgba(76, 175, 80, 0.10),
                inset 0 -3px 12px 0 rgba(76, 175, 80, 0.12),
                0 1px 3px  0 rgba(0,0,0,0.18),
                0 4px 14px 0 rgba(0,0,0,0.10);
            transition: box-shadow 0.25s, transform 0.2s, background 0.2s;
            white-space: nowrap;
        }
        .pz-hover-btn::before {
            content: '';
            position: absolute;
            inset: 0;
            border-radius: inherit;
            pointer-events: none;
            z-index: 1;
            box-shadow:
                inset 0 0 0 1px rgba(165, 214, 167, 0.35),
                inset 0 0 24px 0 rgba(76, 175, 80, 0.08);
            mix-blend-mode: multiply;
            transition: transform 0.3s;
        }
        .pz-hover-btn:hover {
            background: rgba(27, 94, 32, 0.12);
            box-shadow:
                inset 0 0 0 1px rgba(27, 94, 32, 0.35),
                inset 0 0 20px 0  rgba(76, 175, 80, 0.15),
                inset 0 -3px 16px 0 rgba(76, 175, 80, 0.18),
                0 2px 8px  0 rgba(0,0,0,0.22),
                0 8px 24px 0 rgba(27,94,32,0.18);
            transform: translateY(-1px);
        }
        .pz-hover-btn:active::before { transform: scale(0.975); }
        .pz-hover-btn:active        { transform: translateY(0); }

        /* glow circles spawned by JS */
        .pz-hover-btn .pz-hb-circle {
            position: absolute;
            width: 0.75rem; height: 0.75rem;
            border-radius: 50%;
            transform: translate(-50%, -50%);
            filter: blur(10px);
            pointer-events: none;
            z-index: -1;
            opacity: 0;
            transition: opacity 0.3s;
        }
        .pz-hover-btn .pz-hb-circle.fade-in  { opacity: 0.72; }
        .pz-hover-btn .pz-hb-circle.fade-out {
            opacity: 0;
            transition: opacity 1.2s;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Splash Screen ──────────────────────────────────────────────────────────────

def show_splash_screen() -> None:
    """Show a movie-title-card splash screen on first app load this session."""
    if st.session_state.get("_splash_shown"):
        return
    st.session_state["_splash_shown"] = True

    st.markdown(
        """
        <style>
        /* ═══════════════════════════════════════════════════════════
           PULSE-BEAMS SPLASH  (ported from PulseBeams React component)
           Dark slate-950 background · animated gradient beams · PIEZA card
        ═══════════════════════════════════════════════════════════ */
        #pz-splash {
            position: fixed;
            inset: 0;
            background: #020617;
            z-index: 9999999;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            opacity: 1;
            transition: opacity 0.85s ease;
        }
        #pz-splash.pz-splash-out {
            opacity: 0;
            pointer-events: none;
        }

        /* PulseBeams SVG layer — fills the screen, centred */
        #pz-beams {
            position: absolute;
            inset: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            pointer-events: none;
        }
        #pz-beams svg { flex-shrink: 0; }

        /* Centre card — mirrors the "Connect" button in the demo */
        .pz-splash-card {
            position: relative;
            z-index: 10;
            width: clamp(180px, 28vw, 320px);
            height: clamp(90px, 14vw, 120px);
            border-radius: 9999px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: #09090b;
            box-shadow:
                inset 0 0 0 1px rgba(255,255,255,0.08),
                0 0 0 1px rgba(255,255,255,0.05),
                0 25px 50px rgba(0,0,0,0.6);
            opacity: 0;
            animation: pzCardIn 0.75s cubic-bezier(0.16,1,0.3,1) 0.55s both;
        }
        /* Radial glow on hover (replicates the React demo hover state) */
        .pz-splash-card::before {
            content: '';
            position: absolute;
            inset: 0;
            border-radius: inherit;
            background: radial-gradient(75% 100% at 50% 0%,
                rgba(56,189,248,0.55) 0%, rgba(56,189,248,0) 75%);
            opacity: 0;
            transition: opacity 0.5s;
            pointer-events: none;
        }
        .pz-splash-card:hover::before { opacity: 1; }

        .pz-splash-wordmark {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            font-size: clamp(2rem, 5vw, 3.25rem);
            font-weight: 900;
            letter-spacing: -1.5px;
            background: linear-gradient(to right, #cbd5e1, #64748b, #cbd5e1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1;
        }
        .pz-splash-tagline {
            font-size: clamp(0.55rem, 1.2vw, 0.72rem);
            font-weight: 500;
            letter-spacing: 0.22em;
            text-transform: uppercase;
            color: #475569;
            margin-top: 0.3rem;
            font-family: inherit;
        }

        @keyframes pzCardIn {
            from { opacity: 0; transform: scale(0.88); }
            to   { opacity: 1; transform: scale(1); }
        }
        </style>

        <!-- ── PulseBeams splash overlay ───────────────────────────── -->
        <div id="pz-splash">
            <!-- animated beam layer -->
            <div id="pz-beams">
                <svg width="858" height="434" viewBox="0 0 858 434"
                     fill="none" xmlns="http://www.w3.org/2000/svg">

                    <!-- ── base (static) paths ── -->
                    <path d="M269 220.5H16.5C10.9772 220.5 6.5 224.977 6.5 230.5V398.5"
                          stroke="#1e293b" stroke-width="1"/>
                    <path d="M568 200H841C846.523 200 851 195.523 851 190V40"
                          stroke="#1e293b" stroke-width="1"/>
                    <path d="M425.5 274V333C425.5 338.523 421.023 343 415.5 343H152C146.477 343 142 347.477 142 353V426.5"
                          stroke="#1e293b" stroke-width="1"/>
                    <path d="M493 274V333.226C493 338.749 497.477 343.226 503 343.226H760C765.523 343.226 770 347.703 770 353.226V427"
                          stroke="#1e293b" stroke-width="1"/>
                    <path d="M380 168V17C380 11.4772 384.477 7 390 7H414"
                          stroke="#1e293b" stroke-width="1"/>

                    <!-- ── animated (gradient) paths ── -->
                    <path d="M269 220.5H16.5C10.9772 220.5 6.5 224.977 6.5 230.5V398.5"
                          stroke="url(#grad0)" stroke-width="2" stroke-linecap="round"/>
                    <path d="M568 200H841C846.523 200 851 195.523 851 190V40"
                          stroke="url(#grad1)" stroke-width="2" stroke-linecap="round"/>
                    <path d="M425.5 274V333C425.5 338.523 421.023 343 415.5 343H152C146.477 343 142 347.477 142 353V426.5"
                          stroke="url(#grad2)" stroke-width="2" stroke-linecap="round"/>
                    <path d="M493 274V333.226C493 338.749 497.477 343.226 503 343.226H760C765.523 343.226 770 347.703 770 353.226V427"
                          stroke="url(#grad3)" stroke-width="2" stroke-linecap="round"/>
                    <path d="M380 168V17C380 11.4772 384.477 7 390 7H414"
                          stroke="url(#grad4)" stroke-width="2" stroke-linecap="round"/>

                    <!-- ── connection point circles ── -->
                    <circle cx="6.5"   cy="398.5" r="6"   fill="#1e293b" stroke="#334155"/>
                    <circle cx="269"   cy="220.5" r="6"   fill="#1e293b" stroke="#334155"/>
                    <circle cx="851"   cy="34"    r="6.5" fill="#1e293b" stroke="#334155"/>
                    <circle cx="568"   cy="200"   r="6"   fill="#1e293b" stroke="#334155"/>
                    <circle cx="142"   cy="427"   r="6.5" fill="#1e293b" stroke="#334155"/>
                    <circle cx="425.5" cy="274"   r="6"   fill="#1e293b" stroke="#334155"/>
                    <circle cx="770"   cy="427"   r="6.5" fill="#1e293b" stroke="#334155"/>
                    <circle cx="493"   cy="274"   r="6"   fill="#1e293b" stroke="#334155"/>
                    <circle cx="420.5" cy="6.5"   r="6"   fill="#1e293b" stroke="#334155"/>
                    <circle cx="380"   cy="168"   r="6"   fill="#1e293b" stroke="#334155"/>

                    <defs>
                        <!-- gradient stops match the PulseBeams demo colours -->
                        <linearGradient id="grad0" gradientUnits="userSpaceOnUse"
                                        x1="0" x2="0" y1="347" y2="434">
                            <stop offset="0%"   stop-color="#18CCFC" stop-opacity="0"/>
                            <stop offset="20%"  stop-color="#18CCFC" stop-opacity="1"/>
                            <stop offset="50%"  stop-color="#6344F5" stop-opacity="1"/>
                            <stop offset="100%" stop-color="#AE48FF" stop-opacity="0"/>
                        </linearGradient>
                        <linearGradient id="grad1" gradientUnits="userSpaceOnUse"
                                        x1="171" x2="0" y1="347" y2="434">
                            <stop offset="0%"   stop-color="#18CCFC" stop-opacity="0"/>
                            <stop offset="20%"  stop-color="#18CCFC" stop-opacity="1"/>
                            <stop offset="50%"  stop-color="#6344F5" stop-opacity="1"/>
                            <stop offset="100%" stop-color="#AE48FF" stop-opacity="0"/>
                        </linearGradient>
                        <linearGradient id="grad2" gradientUnits="userSpaceOnUse"
                                        x1="171" x2="0" y1="347" y2="434">
                            <stop offset="0%"   stop-color="#18CCFC" stop-opacity="0"/>
                            <stop offset="20%"  stop-color="#18CCFC" stop-opacity="1"/>
                            <stop offset="50%"  stop-color="#6344F5" stop-opacity="1"/>
                            <stop offset="100%" stop-color="#AE48FF" stop-opacity="0"/>
                        </linearGradient>
                        <linearGradient id="grad3" gradientUnits="userSpaceOnUse"
                                        x1="343" x2="429" y1="695" y2="782">
                            <stop offset="0%"   stop-color="#18CCFC" stop-opacity="0"/>
                            <stop offset="20%"  stop-color="#18CCFC" stop-opacity="1"/>
                            <stop offset="50%"  stop-color="#6344F5" stop-opacity="1"/>
                            <stop offset="100%" stop-color="#AE48FF" stop-opacity="0"/>
                        </linearGradient>
                        <linearGradient id="grad4" gradientUnits="userSpaceOnUse"
                                        x1="-343" x2="-86" y1="0" y2="87">
                            <stop offset="0%"   stop-color="#18CCFC" stop-opacity="0"/>
                            <stop offset="20%"  stop-color="#18CCFC" stop-opacity="1"/>
                            <stop offset="50%"  stop-color="#6344F5" stop-opacity="1"/>
                            <stop offset="100%" stop-color="#AE48FF" stop-opacity="0"/>
                        </linearGradient>
                    </defs>
                </svg>
            </div>

            <!-- centred PIEZA title card -->
            <div class="pz-splash-card">
                <div class="pz-splash-wordmark">PIEZA</div>
                <div class="pz-splash-tagline">Family Finance Tracker</div>
            </div>
        </div>

        <script>
        (function () {
            /* ── Beam gradient animation (mirrors framer-motion keyframes) ── */
            var W = 858, H = 434;

            function px(str, isX) {
                return parseFloat(str) / 100 * (isX ? W : H);
            }
            function lerp(a, b, t) { return a + (b - a) * t; }
            function clamp01(t) { return t < 0 ? 0 : t > 1 ? 1 : t; }

            function interp(keys, t) {
                var n = keys.length - 1;
                if (n === 0) return keys[0];
                var seg  = clamp01(t) * n;
                var i    = Math.min(Math.floor(seg), n - 1);
                var f    = seg - i;
                var from = keys[i], to = keys[i + 1];
                return {
                    x1: lerp(from.x1, to.x1, f),
                    x2: lerp(from.x2, to.x2, f),
                    y1: lerp(from.y1, to.y1, f),
                    y2: lerp(from.y2, to.y2, f)
                };
            }

            /* Keyframe configs from the PulseBeams demo */
            var beams = [
                {
                    id: 'grad0',
                    keys: [
                        {x1:'0%',  x2:'0%',   y1:'80%',  y2:'100%'},
                        {x1:'0%',  x2:'0%',   y1:'0%',   y2:'20%'},
                        {x1:'200%',x2:'180%', y1:'0%',   y2:'20%'}
                    ],
                    dur: 2, rDelay: 2, delay: Math.random() * 2
                },
                {
                    id: 'grad1',
                    keys: [
                        {x1:'20%', x2:'0%',   y1:'80%',  y2:'100%'},
                        {x1:'100%',x2:'90%',  y1:'80%',  y2:'100%'},
                        {x1:'100%',x2:'90%',  y1:'-20%', y2:'0%'}
                    ],
                    dur: 2, rDelay: 2, delay: Math.random() * 2
                },
                {
                    id: 'grad2',
                    keys: [
                        {x1:'20%', x2:'0%',   y1:'80%',  y2:'100%'},
                        {x1:'100%',x2:'90%',  y1:'80%',  y2:'100%'},
                        {x1:'100%',x2:'90%',  y1:'-20%', y2:'0%'}
                    ],
                    dur: 2, rDelay: 2, delay: Math.random() * 2
                },
                {
                    id: 'grad3',
                    keys: [
                        {x1:'40%', x2:'50%',  y1:'160%', y2:'180%'},
                        {x1:'0%',  x2:'10%',  y1:'-40%', y2:'-20%'}
                    ],
                    dur: 2, rDelay: 2, delay: Math.random() * 2
                },
                {
                    id: 'grad4',
                    keys: [
                        {x1:'-40%',x2:'-10%', y1:'0%',   y2:'20%'},
                        {x1:'40%', x2:'10%',  y1:'0%',   y2:'20%'},
                        {x1:'0%',  x2:'0%',   y1:'0%',   y2:'20%'},
                        {x1:'0%',  x2:'0%',   y1:'180%', y2:'200%'}
                    ],
                    dur: 2, rDelay: 2, delay: Math.random() * 2
                }
            ];

            beams.forEach(function (cfg) {
                var grad = document.getElementById(cfg.id);
                if (!grad) return;

                /* convert % strings → pixel values */
                var keys = cfg.keys.map(function (k) {
                    return {
                        x1: px(k.x1, true),  x2: px(k.x2, true),
                        y1: px(k.y1, false), y2: px(k.y2, false)
                    };
                });

                var totalMs    = (cfg.dur + cfg.rDelay) * 1000;
                var durationMs = cfg.dur * 1000;
                var origin     = performance.now() + cfg.delay * 1000;

                (function tick(now) {
                    if (now < origin) { requestAnimationFrame(tick); return; }
                    var elapsed = (now - origin) % totalMs;
                    var t       = elapsed < durationMs ? elapsed / durationMs : 1;
                    var v       = interp(keys, t);
                    grad.setAttribute('x1', v.x1.toFixed(1));
                    grad.setAttribute('x2', v.x2.toFixed(1));
                    grad.setAttribute('y1', v.y1.toFixed(1));
                    grad.setAttribute('y2', v.y2.toFixed(1));
                    requestAnimationFrame(tick);
                })(performance.now());
            });

            /* ── Fade-out & remove after 3.4 s ── */
            var splash = document.getElementById('pz-splash');
            if (splash) {
                setTimeout(function () {
                    splash.classList.add('pz-splash-out');
                    setTimeout(function () {
                        if (splash && splash.parentNode)
                            splash.parentNode.removeChild(splash);
                    }, 900);
                }, 3400);
            }
        })();
        </script>
        """,
        unsafe_allow_html=True,
    )


# ── HoverButton helper ─────────────────────────────────────────────────────────

def hover_button_html(label: str, url: str, btn_id: str = "") -> str:
    """
    Return HTML for a HoverButton that navigates to `url` on click.
    Ported from the React HoverButton component — uses the same pointer-tracking
    glow-circle effect via injected JS.

    Usage:
        st.markdown(hover_button_html("Data Entry", "/Data_Entry", "btn-de")
                    + _HOVER_BTN_JS, unsafe_allow_html=True)
    """
    import random, string
    if not btn_id:
        btn_id = "pz-hb-" + "".join(random.choices(string.ascii_lowercase, k=6))
    url_safe = url.replace("'", "\\'")
    return (
        f'<button id="{btn_id}" class="pz-hover-btn" '
        f'onclick="pzNav(\'{url_safe}\')">{label}</button>'
    )


# Shared JS block — inject once per page to wire up all .pz-hover-btn elements
HOVER_BTN_JS = """
<script>
(function () {
    var _lastAdded = 0;

    function _spawnCircle(btn, x, y) {
        var w = btn.offsetWidth || 1;
        var pct = (x / w) * 100;
        var circle = document.createElement('div');
        circle.className = 'pz-hb-circle';
        circle.style.left = x + 'px';
        circle.style.top  = y + 'px';
        circle.style.background =
            'linear-gradient(to right, #a5d6a7 ' + pct + '%, #1b5e20 ' + pct + '%)';
        btn.appendChild(circle);

        requestAnimationFrame(function () {
            circle.classList.add('fade-in');
        });
        setTimeout(function () {
            circle.classList.remove('fade-in');
            circle.classList.add('fade-out');
        }, 1000);
        setTimeout(function () {
            if (circle.parentNode) circle.parentNode.removeChild(circle);
        }, 2200);
    }

    function _attach(btn) {
        btn.addEventListener('pointermove', function (e) {
            var now = Date.now();
            if (now - _lastAdded < 100) return;
            _lastAdded = now;
            var rect = btn.getBoundingClientRect();
            _spawnCircle(btn, e.clientX - rect.left, e.clientY - rect.top);
        });
    }

    function _init() {
        document.querySelectorAll('.pz-hover-btn').forEach(function (b) {
            if (!b._pzHbAttached) {
                b._pzHbAttached = true;
                _attach(b);
            }
        });
    }

    // Re-scan after Streamlit re-renders (polls briefly then stops)
    var _attempts = 0;
    function _poll() {
        _init();
        if (_attempts++ < 20) setTimeout(_poll, 400);
    }
    _poll();
})();
</script>
"""


# ── Navbar / Session ───────────────────────────────────────────────────────────

def _init_session_state() -> None:
    """Initialize all session-state defaults."""
    if "profiles" not in st.session_state:
        st.session_state.profiles = ["Default Family"]
    if "active_profile" not in st.session_state:
        st.session_state.active_profile = st.session_state.profiles[0]
    if "profile_pictures" not in st.session_state:
        st.session_state.profile_pictures = {}
    if "gemini_api_key" not in st.session_state:
        st.session_state.gemini_api_key = st.secrets.get("gemini_api_key", "")
    if "show_add_profile_form" not in st.session_state:
        st.session_state.show_add_profile_form = False


def show_navbar(current_page: str = "Home") -> None:
    """Render the fixed top navbar and handle profile switching via query params."""
    _init_session_state()

    # ── Handle profile-switch query param ──────────────────────────────────────
    params = st.query_params
    if "__pz_profile" in params:
        new_p = params["__pz_profile"]
        if new_p in st.session_state.profiles:
            st.session_state.active_profile = new_p
        del st.query_params["__pz_profile"]
        st.rerun()

    if params.get("__pz_action") == "add_profile":
        st.session_state.show_add_profile_form = True
        del st.query_params["__pz_action"]
        st.rerun()

    active = st.session_state.active_profile
    active_init = active[0].upper() if active else "?"

    # ── Build profile-dropdown HTML ────────────────────────────────────────────
    items_html = ""
    for p in st.session_state.profiles:
        cls = "pz-profile-active" if p == active else ""
        ini = p[0].upper() if p else "?"
        # Use JS-safe escaped name for onclick
        p_safe = p.replace("'", "\\'")
        items_html += f"""
        <div class="pz-profile-item {cls}" onclick="pzSwitch('{p_safe}')">
            <div class="pz-pi-avatar">{ini}</div>
            <span class="pz-pi-name">{p}</span>
            <span class="pz-pi-edit"
                  onclick="event.stopPropagation();pzEditProfile('{p_safe}')"
                  title="Edit profile">&#9998;</span>
        </div>"""

    # ── Build nav links ────────────────────────────────────────────────────────
    pages = [
        ("Home",         "/"),
        ("Data Entry",   "/Data_Entry"),
        ("Transactions", "/Transaction_Ledger"),
        ("AI Advisor",   "/AI_Advisor"),
        ("Loans",        "/Loans_and_Reminders"),
        ("Settings",     "/Settings"),
    ]
    nav_html = ""
    for pname, purl in pages:
        cls = "pz-nav-active" if pname == current_page else ""
        # Use onclick + window.location.assign so navigation stays in the same tab
        nav_html += (
            f'<span class="pz-nav-link {cls}" '
            f'onclick="pzNav(\'{purl}\')" role="link" tabindex="0">'
            f'{pname}</span>'
        )

    st.markdown(
        f"""
        <div class="pz-navbar">
          <!-- Left: logo + profile selector -->
          <div class="pz-nb-left">
            <span class="pz-logo" onclick="pzNav('/')"
                  style="cursor:pointer;">PIEZA</span>
            <div class="pz-profile-selector" onclick="pzToggleDd(event)">
              <div class="pz-ps-avatar">{active_init}</div>
              <span class="pz-ps-name">{active}</span>
              <span class="pz-ps-arrow">&#9660;</span>
            </div>
            <!-- Dropdown panel -->
            <div class="pz-profile-dropdown" id="pz-profile-dd"
                 onclick="event.stopPropagation()">
              {items_html}
              <div class="pz-pi-add" onclick="pzAddProfile()">
                <span style="font-size:1rem;font-weight:800;margin-right:0.45rem;">+</span>
                Add new profile
              </div>
            </div>
          </div>

          <!-- Center: page links -->
          <div class="pz-nb-nav">{nav_html}</div>

          <!-- Right: profile avatar popup -->
          <div class="pz-nb-right">
            <div class="pz-avatar-container">
              <div class="pz-avatar-btn" onclick="pzTogglePP(event)"
                   title="Profile & Settings">{active_init}</div>
              <div class="pz-profile-popup" id="pz-pp"
                   onclick="event.stopPropagation()">
                <div class="pz-pp-avatar">{active_init}</div>
                <div class="pz-pp-name">{active}</div>
                <div class="pz-pp-divider"></div>
                <span class="pz-pp-link" onclick="pzNav('/Settings')"
                      style="cursor:pointer;">Profile &amp; Settings</span>
              </div>
            </div>
          </div>
        </div>

        <script>
        (function(){{
          /* Navigate in the SAME tab — no new windows */
          window.pzNav = function(url) {{
            window.location.assign(url);
          }};

          function closeAll() {{
            var dd = document.getElementById('pz-profile-dd');
            var pp = document.getElementById('pz-pp');
            if(dd) dd.classList.remove('pz-dd-open');
            if(pp) pp.classList.remove('pz-pp-open');
          }}
          document.addEventListener('click', closeAll);

          window.pzToggleDd = function(e) {{
            e.stopPropagation();
            var dd = document.getElementById('pz-profile-dd');
            var pp = document.getElementById('pz-pp');
            if(pp) pp.classList.remove('pz-pp-open');
            if(dd) dd.classList.toggle('pz-dd-open');
          }};
          window.pzTogglePP = function(e) {{
            e.stopPropagation();
            var pp = document.getElementById('pz-pp');
            var dd = document.getElementById('pz-profile-dd');
            if(dd) dd.classList.remove('pz-dd-open');
            if(pp) pp.classList.toggle('pz-pp-open');
          }};
          window.pzSwitch = function(name) {{
            var url = new URL(window.location.href);
            url.searchParams.set('__pz_profile', name);
            window.location.assign(url.toString());
          }};
          window.pzEditProfile = function(name) {{
            var url = new URL(window.location.href);
            url.pathname = '/Settings';
            url.searchParams.set('edit_profile', name);
            window.location.assign(url.toString());
          }};
          window.pzAddProfile = function() {{
            var url = new URL(window.location.href);
            url.searchParams.set('__pz_action', 'add_profile');
            window.location.assign(url.toString());
          }};
        }})();
        </script>
        """,
        unsafe_allow_html=True,
    )

    # ── Inline add-profile form (shown when triggered) ─────────────────────────
    if st.session_state.show_add_profile_form:
        st.markdown('<div class="pz-add-profile-bar">', unsafe_allow_html=True)
        st.markdown("**Add new profile**")
        c1, c2, c3 = st.columns([4, 1, 1])
        with c1:
            new_name = st.text_input(
                "Name", placeholder="Full name…",
                key="_new_profile_name", label_visibility="collapsed",
            )
        with c2:
            if st.button("Add", type="primary", key="_add_profile_btn"):
                if new_name and new_name.strip():
                    n = new_name.strip()
                    if n not in st.session_state.profiles:
                        st.session_state.profiles.append(n)
                        st.session_state.active_profile = n
                    st.session_state.show_add_profile_form = False
                    st.rerun()
        with c3:
            if st.button("Cancel", key="_cancel_add_profile"):
                st.session_state.show_add_profile_form = False
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def show_pagination(page_key: str, total_items: int, items_per_page: int = 20):
    """
    Render a styled pagination bar and return (start_idx, end_idx) for slicing.

    Usage:
        start, end = show_pagination("my_key", len(df))
        st.dataframe(df.iloc[start:end])
    """
    if page_key not in st.session_state:
        st.session_state[page_key] = 1

    total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)
    cur = min(max(1, st.session_state[page_key]), total_pages)
    st.session_state[page_key] = cur

    start_idx = (cur - 1) * items_per_page
    end_idx   = min(start_idx + items_per_page, total_items)

    # ── Build page number list (show up to 7 buttons, with ellipsis) ──────────
    WINDOW = 3  # pages on each side of current
    all_pages = list(range(1, total_pages + 1))
    if total_pages <= 7:
        visible = all_pages
        left_ellipsis = right_ellipsis = False
    else:
        left_ellipsis  = cur > WINDOW + 1
        right_ellipsis = cur < total_pages - WINDOW

        if not left_ellipsis:
            visible = list(range(1, WINDOW * 2 + 2))
        elif not right_ellipsis:
            visible = list(range(total_pages - WINDOW * 2 - 1, total_pages + 1))
        else:
            visible = list(range(cur - WINDOW + 1, cur + WINDOW))

    # ── Render Streamlit button-based pagination ───────────────────────────────
    btn_cols_count = (
        2  # prev + next
        + len(visible)
        + (2 if left_ellipsis else 0)
        + (2 if right_ellipsis else 0)
    )

    cols = st.columns(btn_cols_count, gap="small")
    col_idx = 0

    # Previous
    with cols[col_idx]:
        if st.button("←", key=f"{page_key}_prev", disabled=(cur == 1),
                     help="Previous page"):
            st.session_state[page_key] = cur - 1
            st.rerun()
    col_idx += 1

    # First page + left ellipsis
    if left_ellipsis:
        with cols[col_idx]:
            if st.button("1", key=f"{page_key}_p1"):
                st.session_state[page_key] = 1
                st.rerun()
        col_idx += 1
        with cols[col_idx]:
            st.markdown('<span style="display:flex;align-items:center;justify-content:center;height:2.25rem;color:#888;">…</span>', unsafe_allow_html=True)
        col_idx += 1

    # Page numbers
    for pg in visible:
        with cols[col_idx]:
            is_cur = pg == cur
            label = f"**{pg}**" if is_cur else str(pg)
            btn_type = "primary" if is_cur else "secondary"
            if st.button(label, key=f"{page_key}_pg{pg}", type=btn_type):
                st.session_state[page_key] = pg
                st.rerun()
        col_idx += 1

    # Right ellipsis + last page
    if right_ellipsis:
        with cols[col_idx]:
            st.markdown('<span style="display:flex;align-items:center;justify-content:center;height:2.25rem;color:#888;">…</span>', unsafe_allow_html=True)
        col_idx += 1
        with cols[col_idx]:
            if st.button(str(total_pages), key=f"{page_key}_plast"):
                st.session_state[page_key] = total_pages
                st.rerun()
        col_idx += 1

    # Next
    with cols[col_idx]:
        if st.button("→", key=f"{page_key}_next", disabled=(cur == total_pages),
                     help="Next page"):
            st.session_state[page_key] = cur + 1
            st.rerun()

    st.markdown(
        f'<p class="pz-page-info">Page {cur} of {total_pages} &nbsp;·&nbsp; '
        f'{total_items} item{"s" if total_items != 1 else ""}</p>',
        unsafe_allow_html=True,
    )

    return start_idx, end_idx


def show_global_sidebar() -> None:
    """Backward-compatible alias — now renders the top navbar."""
    show_navbar()


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
        row_date = str(row.get("Date", ""))
        category = str(row.get("Category", ""))
        amount   = row.get("Amount", "")
        options[tx_id] = f"{row_date}  |  {category}  |  {amount}"
    return options


# ── EMI / Loan helpers ─────────────────────────────────────────────────────────

def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """Monthly EMI using the reducing-balance compound-interest formula."""
    if tenure_months <= 0:
        return 0.0
    if annual_rate <= 0:
        return round(principal / tenure_months, 2)
    r = annual_rate / (12 * 100)
    emi = principal * r * (1 + r) ** tenure_months / ((1 + r) ** tenure_months - 1)
    return round(emi, 2)


def _next_emi_date(emi_day: int) -> date:
    """Return the next calendar date on which EMI falls (day-of-month)."""
    today = date.today()
    emi_day = max(1, min(emi_day, 28))
    try:
        candidate = today.replace(day=emi_day)
    except ValueError:
        candidate = today.replace(day=28)
    if candidate >= today:
        return candidate
    # Move to next month
    if today.month == 12:
        return date(today.year + 1, 1, emi_day)
    return date(today.year, today.month + 1, emi_day)


def _get_spreadsheet_obj():
    """Return the raw gspread Spreadsheet object (not cached)."""
    creds_dict = dict(st.secrets["gcp_service_account"])
    client = gspread.service_account_from_dict(creds_dict)
    sheet_name = st.secrets.get("sheet_name", "PIEZA_DB")
    return client.open(sheet_name)


def _get_sheet(title: str, headers: List[str]):
    """Return (or create) a worksheet with the given title and headers."""
    ss = _get_spreadsheet_obj()
    try:
        ws = ss.worksheet(title)
    except gspread.exceptions.WorksheetNotFound:
        ws = ss.add_worksheet(title=title, rows=1000, cols=len(headers))
        ws.append_row(headers)
    return ws


# ── Loans ──────────────────────────────────────────────────────────────────────

def fetch_loans() -> pd.DataFrame:
    """Fetch all loans for the active profile from the Loans worksheet."""
    try:
        ws = _get_sheet("Loans", _LOANS_HEADERS)
        records = ws.get_all_records()
        df = pd.DataFrame(records) if records else pd.DataFrame(columns=_LOANS_HEADERS)
        profile = st.session_state.get("active_profile")
        if profile and "Profile" in df.columns:
            df = df[df["Profile"] == profile]
        return df
    except Exception:
        logger.exception("fetch_loans failed")
        return pd.DataFrame(columns=_LOANS_HEADERS)


def add_loan(loan: Dict[str, Any]) -> bool:
    """Append a loan row to the Loans worksheet."""
    try:
        ws = _get_sheet("Loans", _LOANS_HEADERS)
        row = [loan.get(h, "") for h in _LOANS_HEADERS]
        ws.append_row(row, value_input_option="USER_ENTERED")
        return True
    except Exception:
        logger.exception("add_loan failed")
        st.error("An error occurred while saving the loan. Please check the logs.")
        return False


def delete_loan(loan_ids: List[str]) -> bool:
    """Delete rows whose ID matches any value in loan_ids."""
    try:
        ws = _get_sheet("Loans", _LOANS_HEADERS)
        records = ws.get_all_records()
        id_set = set(str(i) for i in loan_ids)
        rows_to_delete = [
            i + 2  # +1 for header, +1 for 1-based index
            for i, r in enumerate(records)
            if str(r.get("ID", "")) in id_set
        ]
        for row_num in sorted(rows_to_delete, reverse=True):
            ws.delete_rows(row_num)
        return True
    except Exception:
        logger.exception("delete_loan failed")
        st.error("An error occurred while deleting the loan. Please check the logs.")
        return False


# ── Credit cards ───────────────────────────────────────────────────────────────

def fetch_credit_cards() -> pd.DataFrame:
    """Fetch all credit cards for the active profile from the CreditCards worksheet."""
    try:
        ws = _get_sheet("CreditCards", _CARDS_HEADERS)
        records = ws.get_all_records()
        df = pd.DataFrame(records) if records else pd.DataFrame(columns=_CARDS_HEADERS)
        profile = st.session_state.get("active_profile")
        if profile and "Profile" in df.columns:
            df = df[df["Profile"] == profile]
        return df
    except Exception:
        logger.exception("fetch_credit_cards failed")
        return pd.DataFrame(columns=_CARDS_HEADERS)


def add_credit_card(card: Dict[str, Any]) -> bool:
    """Append a credit card row to the CreditCards worksheet."""
    try:
        ws = _get_sheet("CreditCards", _CARDS_HEADERS)
        row = [card.get(h, "") for h in _CARDS_HEADERS]
        ws.append_row(row, value_input_option="USER_ENTERED")
        return True
    except Exception:
        logger.exception("add_credit_card failed")
        st.error("An error occurred while saving the card. Please check the logs.")
        return False


def delete_credit_card(card_ids: List[str]) -> bool:
    """Delete rows whose ID matches any value in card_ids."""
    try:
        ws = _get_sheet("CreditCards", _CARDS_HEADERS)
        records = ws.get_all_records()
        id_set = set(str(i) for i in card_ids)
        rows_to_delete = [
            i + 2
            for i, r in enumerate(records)
            if str(r.get("ID", "")) in id_set
        ]
        for row_num in sorted(rows_to_delete, reverse=True):
            ws.delete_rows(row_num)
        return True
    except Exception:
        logger.exception("delete_credit_card failed")
        st.error("An error occurred while deleting the card. Please check the logs.")
        return False


# ── Reminders ─────────────────────────────────────────────────────────────────

def get_upcoming_reminders(days: int = 7) -> List[Dict[str, Any]]:
    """Return loans and cards with payments due within `days` calendar days."""
    today = date.today()
    reminders: List[Dict[str, Any]] = []

    # Loans
    try:
        loan_df = fetch_loans()
        for _, row in loan_df.iterrows():
            if str(row.get("Status", "")).lower() == "closed":
                continue
            emi_day = int(row.get("EMI Day", 1) or 1)
            next_date = _next_emi_date(emi_day)
            delta = (next_date - today).days
            if 0 <= delta <= days:
                reminders.append({
                    "type": "Loan EMI",
                    "name": row.get("Loan Name", "Loan"),
                    "bank": row.get("Bank", ""),
                    "amount": row.get("EMI Amount", ""),
                    "due_date": next_date,
                    "days_left": delta,
                })
    except Exception:
        pass

    # Credit cards
    try:
        card_df = fetch_credit_cards()
        for _, row in card_df.iterrows():
            if str(row.get("Status", "")).lower() == "closed":
                continue
            raw_due = str(row.get("Due Date", ""))
            try:
                due = date.fromisoformat(raw_due)
            except ValueError:
                continue
            delta = (due - today).days
            if 0 <= delta <= days:
                reminders.append({
                    "type": "Card Payment",
                    "name": row.get("Card Name", "Card"),
                    "bank": row.get("Bank", ""),
                    "amount": row.get("Min Payment", ""),
                    "due_date": due,
                    "days_left": delta,
                })
    except Exception:
        pass

    reminders.sort(key=lambda x: x["due_date"])
    return reminders
