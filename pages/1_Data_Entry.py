import streamlit as st
from utils import show_global_sidebar, parse_gemini_response
import google.generativeai as genai
from PIL import Image
from datetime import datetime

# Page config
st.set_page_config(page_title="Data Entry - PIEZA", layout="wide")

# Show sidebar
show_global_sidebar()

st.title("Data Entry")
st.markdown("Add new transactions manually, or upload a bank screenshot to let AI do the heavy lifting.")

# Initialize draft state for extracted values
if 'draft_tx' not in st.session_state:
    st.session_state.draft_tx = {
        "Date": datetime.today(),
        "Amount": 0.0,
        "Bank Name": "",
        "Type": "Expense",
        "Category": "Groceries"
    }

# Section: Auto-Read Bank Screenshot
st.subheader("Auto-Read Bank Screenshot")

if st.session_state.gemini_api_key:
    uploaded_screenshot = st.file_uploader("Upload Bank Screenshot", type=["png", "jpg", "jpeg"], key="auto_read")
    
    if uploaded_screenshot and st.button("Extract Data with AI"):
        with st.spinner("Extracting data..."):
            try:
                genai.configure(api_key=st.session_state.gemini_api_key)
                # Using gemini-1.5-flash which is standard for multimodal fast tasks
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
                
                # Parse JSON using utility function
                extracted_data = parse_gemini_response(response.text)
                    
                st.session_state.draft_tx = {
                    "Date": extracted_data["Date"],
                    "Amount": extracted_data["Amount"],
                    "Bank Name": extracted_data["Bank Name"],
                    "Type": extracted_data["Type"],
                    "Category": st.session_state.draft_tx.get("Category", "Groceries")
                }
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
    
    with col1:
        tx_type = st.selectbox("Type", ["Income", "Expense"], 
                               index=0 if st.session_state.draft_tx["Type"] == "Income" else 1)
        amount = st.number_input("Amount", min_value=0.0, format="%.2f", step=10.0, 
                                 value=st.session_state.draft_tx["Amount"])
        
        categories = ["Groceries", "Rent", "Loan EMI", "Salary", "Utilities", "Transport", "Entertainment", "Other"]
        category = st.selectbox("Category", categories, 
                                index=categories.index(st.session_state.draft_tx["Category"]) if st.session_state.draft_tx["Category"] in categories else 0)
    
    with col2:
        date_input = st.date_input("Date", st.session_state.draft_tx["Date"])
        bank_name = st.text_input("Bank Name", value=st.session_state.draft_tx["Bank Name"])
        proof_file = st.file_uploader("Upload Receipt/Bill Proof", type=["png", "jpg", "jpeg", "pdf"])

    submit_button = st.form_submit_button("Save Transaction")
    
    if submit_button:
        if amount > 0:
            import uuid
            tx_id = str(uuid.uuid4())
            
            from utils import add_transaction
            
            # Simple proof tracking (just filename/boolean for local test)
            has_proof = bool(proof_file is not None)
            
            # Append to DB
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
                
                # Reset draft state
                st.session_state.draft_tx = {
                    "Date": datetime.today(),
                    "Amount": 0.0,
                    "Bank Name": "",
                    "Type": "Expense",
                    "Category": "Groceries"
                }
        else:
            st.error("Please enter an amount greater than 0.")
