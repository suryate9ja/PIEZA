import streamlit as st
import pandas as pd

from utils import (
    show_global_sidebar,
    fetch_transactions,
    delete_transaction,
    get_bank_domain,
    create_options_map,
)

st.set_page_config(page_title="Ledger - PIEZA", layout="wide")
show_global_sidebar()

st.title("Transaction Ledger")
st.markdown("View all transactions, inspect bank details, and remove incorrect entries.")

# ── Fetch data ─────────────────────────────────────────────────────────────────
df = fetch_transactions()

if df.empty:
    st.info(
        "No transactions found. "
        "Head to Data Entry to add some, or check that your PIEZA_DB sheet "
        "has the correct headers in Row 1: "
        "ID | Profile | Date | Type | Category | Amount | Bank Name | Has Proof"
    )
    st.stop()

# ── Filters ────────────────────────────────────────────────────────────────────
st.subheader("Filters")
col1, col2, col3 = st.columns(3)

with col1:
    profile_options = ["All"] + sorted(df["Profile"].dropna().unique().tolist()) if "Profile" in df.columns else ["All"]
    selected_profile = st.selectbox("Profile", profile_options)

with col2:
    type_options = ["All"] + sorted(df["Type"].dropna().unique().tolist()) if "Type" in df.columns else ["All"]
    selected_type = st.selectbox("Type", type_options)

with col3:
    category_options = ["All"] + sorted(df["Category"].dropna().unique().tolist()) if "Category" in df.columns else ["All"]
    selected_category = st.selectbox("Category", category_options)

filtered_df = df.copy()
if selected_profile != "All" and "Profile" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Profile"] == selected_profile]
if selected_type != "All" and "Type" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Type"] == selected_type]
if selected_category != "All" and "Category" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]

# ── Summary metrics ────────────────────────────────────────────────────────────
if "Amount" in filtered_df.columns and "Type" in filtered_df.columns:
    try:
        filtered_df["Amount"] = pd.to_numeric(filtered_df["Amount"], errors="coerce").fillna(0)
        total_income = filtered_df.loc[filtered_df["Type"] == "Income", "Amount"].sum()
        total_expense = filtered_df.loc[filtered_df["Type"] == "Expense", "Amount"].sum()
        net = total_income - total_expense

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Income", f"{total_income:,.2f}")
        m2.metric("Total Expenses", f"{total_expense:,.2f}")
        m3.metric("Net Balance", f"{net:,.2f}", delta_color="normal")
    except Exception:
        pass

st.markdown("---")

# ── Build display table with bank logos ───────────────────────────────────────
if "Bank Name" in filtered_df.columns:
    filtered_df["Bank Logo"] = filtered_df["Bank Name"].apply(get_bank_domain)

EXPECTED_COLS = [
    "ID", "Profile", "Date", "Bank Logo",
    "Bank Name", "Category", "Type", "Amount", "Has Proof",
]
display_cols = [c for c in EXPECTED_COLS if c in filtered_df.columns]

st.dataframe(
    filtered_df[display_cols],
    use_container_width=True,
    hide_index=True,
    column_config={
        "Date": st.column_config.DateColumn("Date", format="MMM DD, YYYY"),
        "Amount": st.column_config.NumberColumn("Amount", format="%.2f"),
        "Bank Logo": st.column_config.ImageColumn("Bank Logo", help="Powered by Clearbit"),
        "ID": st.column_config.TextColumn("ID", disabled=True),
        "Has Proof": st.column_config.CheckboxColumn("Proof"),
    },
)

st.caption(f"Showing {len(filtered_df)} of {len(df)} transactions.")

st.markdown("---")

# ── Delete Transactions ────────────────────────────────────────────────────────
st.subheader("Manage Transactions")

with st.expander("Delete Transactions"):
    if "ID" not in filtered_df.columns:
        st.warning("Cannot delete: 'ID' column is missing from the database.")
    else:
        options_map = create_options_map(filtered_df)
        tx_ids = filtered_df["ID"].astype(str).tolist()

        selected_ids = st.multiselect(
            "Select transactions to delete",
            options=tx_ids,
            format_func=lambda x: options_map.get(x, x),
        )

        if st.button("Delete Selected", type="primary"):
            if not selected_ids:
                st.warning("Select at least one transaction first.")
            else:
                with st.spinner("Deleting..."):
                    if delete_transaction(selected_ids):
                        st.success(f"Deleted {len(selected_ids)} transaction(s).")
                        st.rerun()
