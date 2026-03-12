import streamlit as st
import uuid
import json
from datetime import datetime
from PIL import Image
import google.generativeai as genai

import pandas as pd
from utils import show_navbar, add_transaction, fetch_transactions, apply_custom_css, show_pagination

st.set_page_config(
    page_title="Data Entry — PIEZA",
    layout="wide",
)
apply_custom_css()
show_navbar("Data Entry")

# ── Page header ────────────────────────────────────────────────────────────────
st.title("Data Entry")
st.markdown(
    "Record transactions manually, or upload a bank screenshot to have "
    "Gemini extract the details for you."
)

# ── Session defaults ───────────────────────────────────────────────────────────
defaults = {
    "form_date":      datetime.today().date(),
    "form_amount":    0.0,
    "form_bank_name": "",
    "form_type":      "Expense",
    "form_category":  "Groceries",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── AI screenshot scanner ──────────────────────────────────────────────────────
st.markdown("---")

st.markdown(
    """
    <div style="
        background:#FFFFFF; border:1px solid #E8F5E9; border-left:4px solid #4CAF50;
        border-radius:10px; padding:1.5rem 1.75rem; margin-bottom:1rem;
        box-shadow:0 1px 4px rgba(27,94,32,0.05);
    ">
        <div style="font-size:0.65rem;font-weight:700;text-transform:uppercase;
                    letter-spacing:0.1em;color:#757575;margin-bottom:0.35rem;">
            AI Scanner
        </div>
        <div style="font-size:1.05rem;font-weight:700;color:#1B5E20;margin-bottom:0.35rem;">
            Extract from bank screenshot
        </div>
        <p style="font-size:0.87rem;color:#555;margin:0;line-height:1.5;">
            Upload a PNG or JPEG of your bank statement and Gemini will
            pre-fill the form below automatically.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.session_state.get("gemini_api_key"):
    uploaded_screenshot = st.file_uploader(
        "Bank screenshot",
        type=["png", "jpg", "jpeg"],
        key="auto_read",
        label_visibility="collapsed",
    )

    if uploaded_screenshot and st.button("Extract data with AI", type="primary"):
        with st.spinner("Reading screenshot with Gemini…"):
            try:
                genai.configure(api_key=st.session_state.gemini_api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                image = Image.open(uploaded_screenshot)

                prompt = """
                Extract the transaction details from this bank screenshot.
                Return ONLY a strict JSON object with these keys:
                - "Date": string in YYYY-MM-DD format
                - "Amount": float (positive number)
                - "Bank Name": string (name of the bank if visible, else "")
                - "Type": string — either "Income" or "Expense"
                No markdown, no explanation, just the JSON.
                """

                response = model.generate_content([prompt, image])
                raw  = response.text.replace("```json", "").replace("```", "").strip()
                data = json.loads(raw)

                try:
                    parsed_date = datetime.strptime(
                        data.get("Date", str(datetime.today().date())), "%Y-%m-%d"
                    ).date()
                except ValueError:
                    parsed_date = datetime.today().date()

                st.session_state.form_date      = parsed_date
                st.session_state.form_amount    = float(data.get("Amount", 0.0))
                st.session_state.form_bank_name = str(data.get("Bank Name", ""))
                type_val = data.get("Type", "Expense")
                st.session_state.form_type = (
                    type_val if type_val in ["Income", "Expense"] else "Expense"
                )

                st.success(
                    "Data extracted successfully. Review the form below before saving."
                )

            except json.JSONDecodeError:
                st.error(
                    "Gemini returned an unexpected response. "
                    "Try uploading a clearer screenshot."
                )
            except Exception as e:
                st.error(f"Extraction failed: {e}")
else:
    st.warning(
        "Add your Gemini API key in **Settings** to enable the AI scanner."
    )

# ── Transaction form ───────────────────────────────────────────────────────────
st.markdown("---")

st.subheader("Review and save transaction")
st.caption(
    "Fields are pre-filled if you used the AI scanner above. "
    "Edit as needed, then click Save."
)

CATEGORIES = [
    "Groceries",
    "Rent",
    "Loan EMI",
    "Salary",
    "Utilities",
    "Transport",
    "Entertainment",
    "Dining",
    "Healthcare",
    "Education",
    "Other",
]

with st.form("manual_entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2, gap="large")

    with col1:
        tx_type = st.selectbox(
            "Transaction type",
            ["Income", "Expense"],
            index=["Income", "Expense"].index(st.session_state.form_type),
        )
        amount = st.number_input(
            "Amount",
            min_value=0.0,
            format="%.2f",
            step=10.0,
            value=float(st.session_state.form_amount),
            help="Enter the transaction amount. Must be greater than 0.",
        )
        category = st.selectbox(
            "Category",
            CATEGORIES,
            index=CATEGORIES.index(st.session_state.form_category)
            if st.session_state.form_category in CATEGORIES
            else 0,
        )

    with col2:
        date_input = st.date_input(
            "Transaction date",
            value=st.session_state.form_date,
        )
        bank_name = st.text_input(
            "Bank or wallet name",
            value=st.session_state.form_bank_name,
            placeholder="e.g. HDFC Bank, PhonePe, Chase",
        )
        proof_file = st.file_uploader(
            "Receipt or bill (optional)",
            type=["png", "jpg", "jpeg", "pdf"],
        )

    submitted = st.form_submit_button("Save transaction", type="primary")

    if submitted:
        if amount <= 0:
            st.error("Amount must be greater than zero. Please enter a valid amount.")
        else:
            tx_data = {
                "ID":        str(uuid.uuid4()),
                "Profile":   st.session_state.active_profile,
                "Date":      date_input.strftime("%Y-%m-%d"),
                "Type":      tx_type,
                "Category":  category,
                "Amount":    amount,
                "Bank Name": bank_name,
                "Has Proof": proof_file is not None,
            }

            if add_transaction(tx_data):
                st.success(
                    f"Transaction saved — "
                    f"{tx_type.lower()}, {category}, {amount:,.2f}."
                )
                st.session_state.form_date      = datetime.today().date()
                st.session_state.form_amount    = 0.0
                st.session_state.form_bank_name = ""
                st.session_state.form_type      = "Expense"
                st.session_state.form_category  = "Groceries"
                # Reset to page 1 so the new entry is visible at the top
                st.session_state["de_recent_page"] = 1

# ── Recent transactions ────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Recent Transactions")
st.caption("Your latest entries — most recent first.")

try:
    hist_df = fetch_transactions()
    if hist_df.empty:
        st.info("No transactions yet. Save your first one above.")
    else:
        # Filter to active profile
        active_profile = st.session_state.get("active_profile", "")
        if active_profile and "Profile" in hist_df.columns:
            hist_df = hist_df[hist_df["Profile"] == active_profile]

        # Sort newest-first (try Date column)
        if "Date" in hist_df.columns:
            try:
                hist_df = hist_df.copy()
                hist_df["_sort_date"] = pd.to_datetime(hist_df["Date"], errors="coerce")
                hist_df = hist_df.sort_values("_sort_date", ascending=False).drop(
                    columns=["_sort_date"]
                )
            except Exception:
                pass

        RECENT_COLS = [c for c in ["Date", "Type", "Category", "Amount", "Bank Name", "Has Proof"]
                       if c in hist_df.columns]

        start, end = show_pagination("de_recent_page", len(hist_df), items_per_page=15)

        st.dataframe(
            hist_df[RECENT_COLS].iloc[start:end],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Date":      st.column_config.DateColumn("Date",  format="DD MMM YYYY"),
                "Amount":    st.column_config.NumberColumn("Amount", format="%.2f"),
                "Has Proof": st.column_config.CheckboxColumn("Has proof"),
            },
        )
except Exception:
    pass
