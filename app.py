import streamlit as st
from utils import show_global_sidebar, apply_custom_css

st.set_page_config(
    page_title="PIEZA - Family Finance Tracker",
    page_icon="assets/logo.png" if __import__("os").path.exists("assets/logo.png") else "💰",
    layout="wide",
)

apply_custom_css()
show_global_sidebar()

# ── Hero section ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="
        background: linear-gradient(135deg, #0f3460 0%, #1565c0 100%);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        margin-bottom: 2rem;
        color: white;
    ">
        <h1 style="color: white; margin: 0; font-size: 2.6rem;">💰 PIEZA</h1>
        <p style="font-size: 1.15rem; margin: 0.4rem 0 0.8rem 0; opacity: 0.9;">
            Family Finance Tracker — know exactly where every rupee goes.
        </p>
        <p style="font-size: 0.9rem; opacity: 0.7; margin: 0;">
            Powered by Google Sheets &nbsp;·&nbsp; AI-driven insights via Gemini
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Active profile banner ──────────────────────────────────────────────────────
active = st.session_state.get("active_profile", "Default Family")
st.info(f"Active profile: **{active}**  — switch profiles in the sidebar.", icon="👤")

st.markdown("---")

# ── Feature cards ─────────────────────────────────────────────────────────────
st.subheader("What would you like to do?")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div style="
            background: white; border-radius: 12px; padding: 1.5rem;
            box-shadow: 0 2px 10px rgba(15,52,96,0.08);
            border-top: 4px solid #2563eb; height: 100%;
        ">
            <h3 style="margin-top: 0; color: #0f3460;">📝 Data Entry</h3>
            <p style="color: #475569; font-size: 0.95rem;">
                Add transactions manually or upload a bank screenshot and let AI
                extract the details for you automatically.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div style="
            background: white; border-radius: 12px; padding: 1.5rem;
            box-shadow: 0 2px 10px rgba(15,52,96,0.08);
            border-top: 4px solid #16a34a; height: 100%;
        ">
            <h3 style="margin-top: 0; color: #0f3460;">📊 Transaction Ledger</h3>
            <p style="color: #475569; font-size: 0.95rem;">
                View, filter, and manage all recorded transactions with live income
                vs. expense summaries and bank logos.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div style="
            background: white; border-radius: 12px; padding: 1.5rem;
            box-shadow: 0 2px 10px rgba(15,52,96,0.08);
            border-top: 4px solid #d97706; height: 100%;
        ">
            <h3 style="margin-top: 0; color: #0f3460;">🤖 AI Advisor</h3>
            <p style="color: #475569; font-size: 0.95rem;">
                Get personalized spending analysis, category breakdowns, and a
                concrete loan-clearing strategy powered by Gemini AI.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ── Quick-start checklist ──────────────────────────────────────────────────────
with st.expander("Quick-start guide", expanded=False):
    st.markdown(
        """
        1. **Add your Gemini API Key** in the sidebar to unlock OCR and AI Advisor features.
        2. **Set up Google Sheets** — create a sheet named `PIEZA_DB` with these column headers in Row 1:
           `ID | Profile | Date | Type | Category | Amount | Bank Name | Has Proof`
        3. **Share the sheet** with your Google service-account email and add the credentials to Streamlit secrets.
        4. **Add your first transaction** on the Data Entry page — manually or via a bank screenshot.
        5. **Explore insights** on the AI Advisor page after adding a few transactions.
        """
    )
