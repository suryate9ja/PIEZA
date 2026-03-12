import streamlit as st
from utils import (
    show_navbar,
    apply_custom_css,
    get_upcoming_reminders,
    show_splash_screen,
    hover_button_html,
    HOVER_BTN_JS,
)

st.set_page_config(
    page_title="PIEZA — Family Finance Tracker",
    page_icon="assets/logo.png" if __import__("os").path.exists("assets/logo.png") else None,
    layout="wide",
)

apply_custom_css()
show_splash_screen()
show_navbar("Home")

# ── Hero ───────────────────────────────────────────────────────────────────────
_hero_btn = hover_button_html("Get Started — Data Entry", "/Data_Entry", "hero-cta")
st.markdown(
    f"""
    <div style="
        background: #FFFFFF;
        border: 1px solid #E8E8E8;
        border-left: 4px solid #1B5E20;
        border-radius: 14px;
        padding: 2.5rem 2.5rem 2.25rem;
        margin-bottom: 2rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05), 0 4px 16px rgba(0,0,0,0.03);
    ">
        <div style="
            font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
            letter-spacing: 0.14em; color: #757575; margin-bottom: 0.55rem;
        ">Personal Finance</div>
        <h1 style="
            color: #1B5E20 !important; font-size: 2.6rem !important;
            font-weight: 800 !important; margin: 0 0 0.5rem !important;
            letter-spacing: -0.8px; line-height: 1.1 !important;
        ">PIEZA</h1>
        <p style="
            color: #444; font-size: 1.05rem; margin: 0 0 1.5rem;
            max-width: 520px; line-height: 1.55;
        ">
            A unified family finance tracker — record every transaction,
            view real-time summaries, and get AI-powered spending advice.
        </p>
        <div style="display:flex; gap:0.85rem; flex-wrap:wrap; align-items:center;
                    margin-bottom:1.25rem;">
            {_hero_btn}
        </div>
        <div style="display:flex; gap:0.65rem; flex-wrap:wrap;">
            <span style="
                background: #EBF5EB; color: #1B5E20;
                padding: 0.28rem 0.8rem; border-radius: 20px;
                font-size: 0.76rem; font-weight: 600; letter-spacing: 0.04em;
                border: 1px solid #A5D6A7;
            ">Google Sheets</span>
            <span style="
                background: #EBF5EB; color: #1B5E20;
                padding: 0.28rem 0.8rem; border-radius: 20px;
                font-size: 0.76rem; font-weight: 600; letter-spacing: 0.04em;
                border: 1px solid #A5D6A7;
            ">Gemini AI</span>
            <span style="
                background: #EBF5EB; color: #1B5E20;
                padding: 0.28rem 0.8rem; border-radius: 20px;
                font-size: 0.76rem; font-weight: 600; letter-spacing: 0.04em;
                border: 1px solid #A5D6A7;
            ">Multi-profile</span>
        </div>
    </div>
    {HOVER_BTN_JS}
    """,
    unsafe_allow_html=True,
)

# ── Active profile notice ──────────────────────────────────────────────────────
active = st.session_state.get("active_profile", "Default Family")
st.info(f"Viewing as **{active}**.  Switch profiles from the dropdown in the top navbar.")

st.markdown("---")

# ── Upcoming reminders banner ──────────────────────────────────────────────────
try:
    reminders = get_upcoming_reminders(days=7)
    if reminders:
        st.markdown(
            '<p class="section-label">Upcoming payments (next 7 days)</p>',
            unsafe_allow_html=True,
        )
        for r in reminders:
            days = r["days_left"]
            label = "today" if days == 0 else f"in {days} day(s)"
            urgency_color = "#C62828" if days <= 1 else ("#E65100" if days <= 3 else "#1B5E20")
            st.markdown(
                f"""
                <div style="
                    background:#FFFFFF; border:1px solid #E8E8E8;
                    border-left:4px solid {urgency_color};
                    border-radius:8px; padding:0.75rem 1.2rem;
                    margin-bottom:0.5rem;
                    box-shadow:0 1px 3px rgba(0,0,0,0.05);
                    display:flex; justify-content:space-between; align-items:center;
                ">
                    <div>
                        <span style="font-weight:700;color:#1A1A1A;">{r['name']}</span>
                        <span style="color:#757575;font-size:0.85rem;margin-left:0.5rem;">
                            {r['type']} — {r['bank']}
                        </span>
                    </div>
                    <div style="text-align:right;">
                        <span style="font-weight:700;color:{urgency_color};">Due {label}</span>
                        <span style="color:#555;font-size:0.85rem;margin-left:0.75rem;">
                            {r['due_date'].strftime('%d %b %Y')}
                        </span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("---")
except Exception:
    pass

# ── Feature cards ─────────────────────────────────────────────────────────────
st.subheader("Where would you like to go?")
st.markdown(" ")

card_style = """
    background: #FFFFFF;
    border: 1px solid #E8E8E8;
    border-top: 3px solid {accent};
    border-radius: 12px;
    padding: 1.6rem 1.5rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05), 0 4px 14px rgba(0,0,0,0.03);
    height: 100%;
"""

_btn_de  = hover_button_html("Go to Data Entry",        "/Data_Entry",          "fc-de")
_btn_tl  = hover_button_html("Go to Ledger",            "/Transaction_Ledger",  "fc-tl")
_btn_ai  = hover_button_html("Go to AI Advisor",        "/AI_Advisor",          "fc-ai")
_btn_ln  = hover_button_html("Go to Loans",             "/Loans_and_Reminders", "fc-ln")
_btn_cfg = hover_button_html("Go to Settings",          "/Settings",            "fc-cfg")

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown(
        f"""
        <div style="{card_style.format(accent='#1B5E20')}">
            <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.1em;color:#757575;margin-bottom:0.6rem;">
                Step 1
            </div>
            <div style="font-size:1.05rem;font-weight:700;color:#1A1A1A;
                        margin-bottom:0.5rem;">
                Data Entry
            </div>
            <p style="font-size:0.87rem;color:#555;line-height:1.55;margin:0 0 1rem;">
                Record transactions manually or upload a bank screenshot
                and let AI extract the details automatically.
            </p>
            {_btn_de}
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div style="{card_style.format(accent='#388E3C')}">
            <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.1em;color:#757575;margin-bottom:0.6rem;">
                Step 2
            </div>
            <div style="font-size:1.05rem;font-weight:700;color:#1A1A1A;
                        margin-bottom:0.5rem;">
                Transaction Ledger
            </div>
            <p style="font-size:0.87rem;color:#555;line-height:1.55;margin:0 0 1rem;">
                View, filter, and manage all recorded transactions with
                live income vs. expense summaries and bank logos.
            </p>
            {_btn_tl}
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div style="{card_style.format(accent='#4CAF50')}">
            <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.1em;color:#757575;margin-bottom:0.6rem;">
                Step 3
            </div>
            <div style="font-size:1.05rem;font-weight:700;color:#1A1A1A;
                        margin-bottom:0.5rem;">
                AI Financial Advisor
            </div>
            <p style="font-size:0.87rem;color:#555;line-height:1.55;margin:0 0 1rem;">
                Get personalized spending analysis, category breakdowns,
                and a concrete loan-clearing strategy powered by Gemini.
            </p>
            {_btn_ai}
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(" ")
col4, col5, _ = st.columns(3, gap="large")

with col4:
    st.markdown(
        f"""
        <div style="{card_style.format(accent='#2E7D32')}">
            <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.1em;color:#757575;margin-bottom:0.6rem;">
                Step 4
            </div>
            <div style="font-size:1.05rem;font-weight:700;color:#1A1A1A;
                        margin-bottom:0.5rem;">
                Loans &amp; Reminders
            </div>
            <p style="font-size:0.87rem;color:#555;line-height:1.55;margin:0 0 1rem;">
                Track EMIs and credit card due dates with automated
                upcoming-payment reminders.
            </p>
            {_btn_ln}
        </div>
        """,
        unsafe_allow_html=True,
    )

with col5:
    st.markdown(
        f"""
        <div style="{card_style.format(accent='#66BB6A')}">
            <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.1em;color:#757575;margin-bottom:0.6rem;">
                Setup
            </div>
            <div style="font-size:1.05rem;font-weight:700;color:#1A1A1A;
                        margin-bottom:0.5rem;">
                Settings
            </div>
            <p style="font-size:0.87rem;color:#555;line-height:1.55;margin:0 0 1rem;">
                Configure your Gemini API key, manage family profiles,
                and connect your Google Sheet.
            </p>
            {_btn_cfg}
        </div>
        """,
        unsafe_allow_html=True,
    )

# Wire up hover-button JS for all cards (single injection)
st.markdown(HOVER_BTN_JS, unsafe_allow_html=True)

st.markdown("---")

# ── Quick-start guide ──────────────────────────────────────────────────────────
with st.expander("Quick-start guide"):
    st.markdown(
        """
        **Before you begin**

        1. Add your **Gemini API key** in the **Settings** page to unlock the AI scanner and Advisor.
        2. Ensure your Google Sheet (`PIEZA_DB`) has these exact column headers in Row 1:

           `ID` &nbsp;|&nbsp; `Profile` &nbsp;|&nbsp; `Date` &nbsp;|&nbsp;
           `Type` &nbsp;|&nbsp; `Category` &nbsp;|&nbsp; `Amount` &nbsp;|&nbsp;
           `Bank Name` &nbsp;|&nbsp; `Has Proof`

        3. Share the sheet with your service account email and add the credentials
           to `.streamlit/secrets.toml` under `[gcp_service_account]`.
        4. Select a family member profile in the navbar dropdown, then head to **Data Entry**
           to record your first transaction.
        5. Once a few entries exist, visit **AI Financial Advisor** for insights.
        """
    )
