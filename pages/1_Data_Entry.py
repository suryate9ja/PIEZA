import streamlit as st
import uuid
import json
from datetime import datetime
from PIL import Image
import google.generativeai as genai

from utils import show_global_sidebar, add_transaction, apply_custom_css

st.set_page_config(page_title="Data Entry - PIEZA", layout="wide", page_icon="📝")
apply_custom_css()
show_global_sidebar()

st.title("📝 Data Entry")
st.markdown(
    "Add transactions manually, or upload a bank screenshot to let AI extract the details."
)

# ── Session state defaults for form fields ─────────────────────────────────────
defaults = {
    "form_date": datetime.today().date(),
    "form_amount": 0.0,
    "form_bank_name": "",
    "form_type": "Expense",
    "form_category": "Groceries",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── AI Screenshot Scanner ──────────────────────────────────────────────────────
st.markdown("---")

with st.container():
    st.subheader("🤖 AI Screenshot Scanner")
    st.caption("Upload a bank statement screenshot and Gemini will pre-fill the form below.")

    if st.session_state.get("gemini_api_key"):
        uploaded_screenshot = st.file_uploader(
            "Bank screenshot (PNG / JPG / JPEG)",
            type=["png", "jpg", "jpeg"],
            key="auto_read",
        )

        if uploaded_screenshot and st.button("Extract Data with AI", type="primary"):
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
                    raw = response.text.replace("```json", "").replace("```", "").strip()
                    data = json.loads(raw)

                    try:
                        parsed_date = datetime.strptime(
                            data.get("Date", str(datetime.today().date())), "%Y-%m-%d"
                        ).date()
                    except ValueError:
                        parsed_date = datetime.today().date()

                    st.session_state.form_date = parsed_date
                    st.session_state.form_amount = float(data.get("Amount", 0.0))
                    st.session_state.form_bank_name = str(data.get("Bank Name", ""))
                    type_val = data.get("Type", "Expense")
                    st.session_state.form_type = (
                        type_val if type_val in ["Income", "Expense"] else "Expense"
                    )

                    st.success("Data extracted successfully. Review the form below before saving.")

                except json.JSONDecodeError:
                    st.error(
                        "AI returned unexpected output. Try uploading a clearer screenshot."
                    )
                except Exception as e:
                    st.error(f"Extraction failed: {e}")
    else:
        st.warning(
            "Configure your **Gemini API Key** in the sidebar to use the AI scanner.",
            icon="🔑",
        )

# ── Manual / Review Form ───────────────────────────────────────────────────────
st.markdown("---")

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

st.subheader("📋 Review and Save Transaction")
st.caption(
    "Fields below are pre-filled if you used the AI scanner. "
    "Edit as needed, then click **Save Transaction**."
)

with st.form("manual_entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        tx_type = st.selectbox(
            "Transaction Type",
            ["Income", "Expense"],
            index=["Income", "Expense"].index(st.session_state.form_type),
        )
        amount = st.number_input(
            "Amount",
            min_value=0.0,
            format="%.2f",
            step=10.0,
            value=float(st.session_state.form_amount),
            help="Enter the transaction amount (must be greater than 0).",
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
            "Transaction Date", value=st.session_state.form_date
        )
        bank_name = st.text_input(
            "Bank / Wallet Name",
            value=st.session_state.form_bank_name,
            placeholder="e.g. HDFC, Chase, PhonePe",
        )
        proof_file = st.file_uploader(
            "Receipt / Bill Proof (optional)",
            type=["png", "jpg", "jpeg", "pdf"],
        )

    submitted = st.form_submit_button("💾 Save Transaction", type="primary")

    if submitted:
        if amount <= 0:
            st.error("Amount must be greater than 0. Please enter a valid amount.")
        else:
            tx_data = {
                "ID": str(uuid.uuid4()),
                "Profile": st.session_state.active_profile,
                "Date": date_input.strftime("%Y-%m-%d"),
                "Type": tx_type,
                "Category": category,
                "Amount": amount,
                "Bank Name": bank_name,
                "Has Proof": proof_file is not None,
            }

            if add_transaction(tx_data):
                st.success(
                    f"Transaction saved successfully to Google Sheets! "
                    f"({tx_type} · {category} · {amount:,.2f})"
                )
                # Reset form defaults
                st.session_state.form_date = datetime.today().date()
                st.session_state.form_amount = 0.0
                st.session_state.form_bank_name = ""
                st.session_state.form_type = "Expense"
                st.session_state.form_category = "Groceries"
