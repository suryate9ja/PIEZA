import streamlit as st
import uuid
import json
from datetime import datetime
from PIL import Image
import google.generativeai as genai

from utils import show_global_sidebar, add_transaction

st.set_page_config(page_title="Data Entry - PIEZA", layout="wide")
show_global_sidebar()

st.title("Data Entry")
st.markdown("Add transactions manually, or upload a bank screenshot to let AI extract the details.")

# ── Session state defaults for the form fields ─────────────────────────────────
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

# ── Auto-Read Bank Screenshot ──────────────────────────────────────────────────
st.subheader("Auto-Read Bank Screenshot")

if st.session_state.gemini_api_key:
    uploaded_screenshot = st.file_uploader(
        "Upload Bank Screenshot", type=["png", "jpg", "jpeg"], key="auto_read"
    )

    if uploaded_screenshot and st.button("Extract Data with AI"):
        with st.spinner("Reading screenshot..."):
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
                st.session_state.form_type = type_val if type_val in ["Income", "Expense"] else "Expense"

                st.success("Data extracted. Review the form below before saving.")

            except json.JSONDecodeError:
                st.error("AI returned unexpected output. Try a clearer screenshot.")
            except Exception as e:
                st.error(f"Extraction failed: {e}")
else:
    st.warning("Configure your Gemini API Key in the sidebar to use this feature.")

st.markdown("---")

# ── Manual / Review Form ───────────────────────────────────────────────────────
st.subheader("Review and Save Transaction")

CATEGORIES = [
    "Groceries", "Rent", "Loan EMI", "Salary",
    "Utilities", "Transport", "Entertainment",
    "Dining", "Healthcare", "Education", "Other",
]

with st.form("manual_entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)

    with col1:
        tx_type = st.selectbox(
            "Type", ["Income", "Expense"],
            index=["Income", "Expense"].index(st.session_state.form_type),
        )
        amount = st.number_input(
            "Amount", min_value=0.0, format="%.2f", step=10.0,
            value=float(st.session_state.form_amount),
        )
        category = st.selectbox(
            "Category", CATEGORIES,
            index=CATEGORIES.index(st.session_state.form_category)
            if st.session_state.form_category in CATEGORIES else 0,
        )

    with col2:
        date_input = st.date_input("Date", value=st.session_state.form_date)
        bank_name = st.text_input("Bank Name", value=st.session_state.form_bank_name)
        proof_file = st.file_uploader(
            "Upload Receipt / Bill Proof",
            type=["png", "jpg", "jpeg", "pdf"],
        )

    submitted = st.form_submit_button("Save Transaction")

    if submitted:
        if amount <= 0:
            st.error("Amount must be greater than 0.")
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
                st.success("Transaction saved to Google Sheets.")
                # Reset form defaults
                st.session_state.form_date = datetime.today().date()
                st.session_state.form_amount = 0.0
                st.session_state.form_bank_name = ""
                st.session_state.form_type = "Expense"
                st.session_state.form_category = "Groceries"
