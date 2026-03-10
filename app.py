import streamlit as st
from utils import show_global_sidebar, apply_custom_css

st.set_page_config(
    page_title="PIEZA — Family Finance Tracker",
    page_icon="assets/logo.png" if __import__("os").path.exists("assets/logo.png") else None,
    layout="wide",
)

apply_custom_css()
show_global_sidebar()

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="
        background: linear-gradient(135deg, #14401C 0%, #1B5E20 50%, #2E7D32 100%);
        border-radius: 14px;
        padding: 2.75rem 2.5rem 2.5rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute; top: -30px; right: -30px;
            width: 200px; height: 200px; border-radius: 50%;
            background: rgba(255,255,255,0.04);
        "></div>
        <div style="
            position: absolute; bottom: -50px; right: 80px;
            width: 140px; height: 140px; border-radius: 50%;
            background: rgba(255,255,255,0.03);
        "></div>
        <div style="position: relative; z-index: 1;">
            <div style="
                font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
                letter-spacing: 0.14em; color: #81C784; margin-bottom: 0.6rem;
            ">Personal Finance</div>
            <h1 style="
                color: #FFFFFF !important; font-size: 2.6rem !important;
                font-weight: 800 !important; margin: 0 0 0.5rem !important;
                letter-spacing: -0.8px; line-height: 1.1 !important;
            ">PIEZA</h1>
            <p style="
                color: #C8E6C9; font-size: 1.05rem; margin: 0 0 1.5rem;
                max-width: 520px; line-height: 1.55;
            ">
                A unified family finance tracker — record every transaction,
                view real-time summaries, and get AI-powered spending advice.
            </p>
            <div style="display:flex; gap:0.75rem; flex-wrap:wrap;">
                <span style="
                    background: rgba(255,255,255,0.12); color: #E8F5E9;
                    padding: 0.3rem 0.85rem; border-radius: 20px;
                    font-size: 0.76rem; font-weight: 600; letter-spacing: 0.04em;
                    border: 1px solid rgba(255,255,255,0.18);
                ">Google Sheets</span>
                <span style="
                    background: rgba(255,255,255,0.12); color: #E8F5E9;
                    padding: 0.3rem 0.85rem; border-radius: 20px;
                    font-size: 0.76rem; font-weight: 600; letter-spacing: 0.04em;
                    border: 1px solid rgba(255,255,255,0.18);
                ">Gemini AI</span>
                <span style="
                    background: rgba(255,255,255,0.12); color: #E8F5E9;
                    padding: 0.3rem 0.85rem; border-radius: 20px;
                    font-size: 0.76rem; font-weight: 600; letter-spacing: 0.04em;
                    border: 1px solid rgba(255,255,255,0.18);
                ">Multi-profile</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Active profile notice ──────────────────────────────────────────────────────
active = st.session_state.get("active_profile", "Default Family")
st.info(
    f"Viewing as **{active}**.  Switch profiles anytime from the sidebar.",
    icon=None,
)

st.markdown("---")

# ── Feature cards ─────────────────────────────────────────────────────────────
st.subheader("Where would you like to go?")
st.markdown(" ")

card_style = """
    background: #FFFFFF;
    border: 1px solid #E8F5E9;
    border-top: 3px solid {accent};
    border-radius: 12px;
    padding: 1.6rem 1.5rem;
    box-shadow: 0 1px 4px rgba(27,94,32,0.06), 0 4px 14px rgba(27,94,32,0.04);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    height: 100%;
"""

col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown(
        f"""
        <div style="{card_style.format(accent='#2E7D32')}">
            <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.1em;color:#757575;margin-bottom:0.6rem;">
                Step 1
            </div>
            <div style="font-size:1.05rem;font-weight:700;color:#1B5E20;
                        margin-bottom:0.5rem;">
                Data Entry
            </div>
            <p style="font-size:0.87rem;color:#555;line-height:1.55;margin:0;">
                Record transactions manually or upload a bank screenshot
                and let AI extract the details automatically.
            </p>
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
            <div style="font-size:1.05rem;font-weight:700;color:#1B5E20;
                        margin-bottom:0.5rem;">
                Transaction Ledger
            </div>
            <p style="font-size:0.87rem;color:#555;line-height:1.55;margin:0;">
                View, filter, and manage all recorded transactions with
                live income vs. expense summaries and bank logos.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div style="{card_style.format(accent='#43A047')}">
            <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.1em;color:#757575;margin-bottom:0.6rem;">
                Step 3
            </div>
            <div style="font-size:1.05rem;font-weight:700;color:#1B5E20;
                        margin-bottom:0.5rem;">
                AI Financial Advisor
            </div>
            <p style="font-size:0.87rem;color:#555;line-height:1.55;margin:0;">
                Get personalized spending analysis, category breakdowns,
                and a concrete loan-clearing strategy powered by Gemini.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Quick-start guide ──────────────────────────────────────────────────────────
with st.expander("Quick-start guide"):
    st.markdown(
        """
        **Before you begin**

        1. Add your **Gemini API key** in the sidebar to unlock the AI scanner and Advisor.
        2. Ensure your Google Sheet (`PIEZA_DB`) has these exact column headers in Row 1:

           `ID` &nbsp;|&nbsp; `Profile` &nbsp;|&nbsp; `Date` &nbsp;|&nbsp;
           `Type` &nbsp;|&nbsp; `Category` &nbsp;|&nbsp; `Amount` &nbsp;|&nbsp;
           `Bank Name` &nbsp;|&nbsp; `Has Proof`

        3. Share the sheet with your service account email and add the credentials
           to `.streamlit/secrets.toml` under `[gcp_service_account]`.
        4. Select a family member profile in the sidebar, then head to **Data Entry**
           to record your first transaction.
        5. Once a few entries exist, visit **AI Financial Advisor** for insights.
        """
    )
