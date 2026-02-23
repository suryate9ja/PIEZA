import streamlit as st
import uuid
import json
from datetime import datetime
from PIL import Image
import google.generativeai as genai

from utils import show_global_sidebar, add_transaction

# Page config
st.set_page_config(page_title="Data Entry - PIEZA", layout="wide")

# Show sidebar
show_global_sidebar()

st.title("Data Entry")
st.markdown("Add new transactions manually, or upload a bank screenshot to let AI do the heavy lifting.")

# Initialize form widget states directly in session_state instead of a draft dictionary
if 'form_date' not in st.session_state:
    st.session_state.form_date = datetime.today()
if 'form_amount' not in st.session_state:
    st.session_state.form_amount = 0.0
if 'form_bank_name' not in st.session_state:
    st.session_state.form_bank_name = ""
if 'form_type' not in st.session_state:
    st.session_state.form_type = "Expense"
if 'form_category' not in st.session_state:
    st.session_state.form_category = "Groceries"

# Section: Auto-Read Bank Screenshot
st.subheader("Auto-Read Bank Screenshot")

if st.session_state.gemini_api_key:
    uploaded_screenshot = st.file_uploader("Upload Bank Screenshot", type=["png", "jpg", "jpeg"], key="auto_read")
    
    if uploaded_screenshot and st.button("Extract Data with AI"):
        with st.spinner("Extracting data..."):
            try:
                genai.configure(api_key=st.session_state.gemini_api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                image = Image.open(uploaded_screenshot)
                prompt = """
                Extract the transaction details from this bank screenshot and output them as a strict JSON object.
                Keys required:
                - "Date": string (format YYYY-MM-DD)
                - "Amount": float (the transaction amount, positive number)
                - "Bank Name": string (guess the bank name if visible, else "")
                - "Type": string (either "Income" or "Expense")
                
                Return ONLY the JSON. No markdown formatting.
                """
                
                response = model.generate_content([prompt, image])
                
                raw_text = response.text.replace("```json", "").replace("```", "").strip()
                extracted_data = json.loads(raw_text)
                
                try:
                    parsed_date = datetime.strptime(extracted_data.get("Date", str(datetime.today().date())), "%Y-%m-%d").date()
                except ValueError:
                    parsed_date = datetime.today().date()
                
                # Update widget states directly
                st.session_state.form_date = parsed_date
                st.session_state.form_amount = float(extracted_data.get("Amount", 0.0))
                st.session_state.form_bank_name = str(extracted_data.get("Bank Name", ""))
                
                type_val = str(extracted_data.get("Type", "Expense"))
                if type_val in ["Income", "Expense"]:
                    st.session_state.form_type = type_val
                    
                st.success("Data extracted successfully! Please review below.")
            except Exception as e:
                st.error(f"Error extracting data: {e}")
else:
    st.warning("Please configure your Gemini API Key in the sidebar to use the auto-read feature.")

st.markdown("---")

# Section: Manual Input
st.subheader("Review & Save Transaction")

with st.form("manual_entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    categories = ["Groceries", "Rent", "Loan EMI", "Salary", "Utilities", "Transport", "Entertainment", "Other"]
    
    with col1:
        # Binding directly to session_state using `key`
        tx_type = st.selectbox("Type", ["Income", "Expense"], key="form_type")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f", step=10.0, key="form_amount")
        category = st.selectbox("Category", categories, key="form_category")
    
    with col2:
        date_input = st.date_input("Date", key="form_date")
        bank_name = st.text_input("Bank Name", key="form_bank_name")
        proof_file = st.file_uploader("Upload Receipt/Bill Proof", type=["png", "jpg", "jpeg", "pdf"], key="form_proof")

    submit_button = st.form_submit_button("Save Transaction")
    
    if submit_button:
        if amount > 0:
            tx_id = str(uuid.uuid4())
            has_proof = bool(proof_file is not None)
            
            tx_data = {
                "ID": tx_id,
                "Profile": st.session_state.active_profile,
                "Date": date_input.strftime("%Y-%m-%d"),
                "Type": tx_type,
                "Category": category,
                "Amount": amount,
                "Bank Name": bank_name,
                "Has Proof": has_proof
            }
            
            if add_transaction(tx_data):
                st.success("Transaction saved successfully to Google Sheets!")
                
                # Reset widget states
                st.session_state.form_date = datetime.today()
                st.session_state.form_amount = 0.0
                st.session_state.form_bank_name = ""
                st.session_state.form_type = "Expense"
                st.session_state.form_category = "Groceries"
        else:
            st.error("Please enter an amount greater than 0.")
