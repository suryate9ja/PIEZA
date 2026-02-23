import streamlit as st
import pandas as pd
from utils import show_global_sidebar, fetch_transactions, delete_transaction, get_bank_domain

# Page config
st.set_page_config(page_title="Ledger - PIEZA", layout="wide")

# Show sidebar
show_global_sidebar()

st.title("Transaction Ledger")
st.markdown("View all your recent transactions, track your banks, and manage your data.")

# Fetch directly from Google Sheets
df = fetch_transactions()

if df.empty:
    st.info("No transactions found. Go to the Data Entry page to add some, or ensure your Google Sheet 'PIEZA_DB' has correct headers in Row 1.")
else:
    df["Bank Logo"] = df["Bank Name"].apply(get_bank_domain)
    
    # Reorder columns for display
    # Verify cols exist first to prevent crashes on empty sheets with wrong headers
    expected_cols = ["ID", "Profile", "Date", "Bank Logo", "Bank Name", "Category", "Type", "Amount", "Has Proof"]
    display_cols = [c for c in expected_cols if c in df.columns]
    
    df_display = df[display_cols]
    
    st.dataframe(
        df_display, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Date": st.column_config.DateColumn("Date", format="MMM DD, YYYY"),
            "Amount": st.column_config.NumberColumn("Amount", format="%.2f"),
            "Bank Logo": st.column_config.ImageColumn("Bank Logo", help="Provided by ClearBit"),
            "ID": st.column_config.TextColumn("ID", disabled=True)
        }
    )
    
    st.markdown("---")
    
    # Delete Mechanism
    st.subheader("Manage Transactions")
    with st.expander("Delete Transactions"):
        if "ID" in df.columns:
            tx_ids = df["ID"].astype(str).tolist()
            
            # Create a dictionary mapping ID to a readable string for the multiselect
            options_map = {}
            for _, row in df.iterrows():
                try: # handle missing columns gracefully
                    options_map[str(row["ID"])] = f"{row.get('Date','')} - {row.get('Category','')} - {row.get('Amount','')} ({row.get('Type','')})"
                except Exception:
                    options_map[str(row["ID"])] = str(row["ID"])
            
            selected_ids = st.multiselect(
                "Select transactions to delete:", 
                options=tx_ids, 
                format_func=lambda x: options_map.get(x, x)
            )
            
            if st.button("Delete Selected", type="primary"):
                if selected_ids:
                    with st.spinner("Deleting from Google Sheets..."):
                        if delete_transaction(selected_ids):
                            st.success(f"Deleted {len(selected_ids)} transactions!")
                            st.rerun()
                else:
                    st.warning("Please select at least one transaction to delete.")
        else:
            st.warning("Cannot delete transactions. 'ID' column is missing from the database.")
