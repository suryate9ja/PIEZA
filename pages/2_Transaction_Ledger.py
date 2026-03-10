import streamlit as st
import pandas as pd

from utils import (
    show_global_sidebar,
    fetch_transactions,
    delete_transaction,
    get_bank_domain,
    create_options_map,
    apply_custom_css,
)

st.set_page_config(
    page_title="Transaction Ledger — PIEZA",
    layout="wide",
)
apply_custom_css()
show_global_sidebar()

# ── Page header ────────────────────────────────────────────────────────────────
st.title("Transaction Ledger")
st.markdown(
    "View, filter, and manage all recorded transactions with "
    "live income and expense summaries."
)

# ── Fetch data ─────────────────────────────────────────────────────────────────
df = fetch_transactions()

if df.empty:
    st.markdown("---")
    st.info(
        "No transactions found yet.  "
        "Go to **Data Entry** to record your first transaction, or confirm that "
        "your `PIEZA_DB` sheet has the correct column headers in Row 1:  \n"
        "`ID | Profile | Date | Type | Category | Amount | Bank Name | Has Proof`"
    )
    st.stop()

# ── Filters ────────────────────────────────────────────────────────────────────
st.markdown("---")

st.markdown(
    '<p class="section-label">Filters</p>',
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    profile_opts = (
        ["All"] + sorted(df["Profile"].dropna().unique().tolist())
        if "Profile" in df.columns else ["All"]
    )
    selected_profile = st.selectbox("Profile", profile_opts)

with col2:
    type_opts = (
        ["All"] + sorted(df["Type"].dropna().unique().tolist())
        if "Type" in df.columns else ["All"]
    )
    selected_type = st.selectbox("Type", type_opts)

with col3:
    cat_opts = (
        ["All"] + sorted(df["Category"].dropna().unique().tolist())
        if "Category" in df.columns else ["All"]
    )
    selected_category = st.selectbox("Category", cat_opts)

filtered_df = df.copy()
if selected_profile != "All" and "Profile" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Profile"] == selected_profile]
if selected_type != "All" and "Type" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Type"] == selected_type]
if selected_category != "All" and "Category" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]

# ── Summary metrics ────────────────────────────────────────────────────────────
st.markdown("---")

if "Amount" in filtered_df.columns and "Type" in filtered_df.columns:
    try:
        filtered_df["Amount"] = pd.to_numeric(
            filtered_df["Amount"], errors="coerce"
        ).fillna(0)
        total_income  = filtered_df.loc[filtered_df["Type"] == "Income",  "Amount"].sum()
        total_expense = filtered_df.loc[filtered_df["Type"] == "Expense", "Amount"].sum()
        net           = total_income - total_expense

        m1, m2, m3, m4 = st.columns(4, gap="medium")
        m1.metric("Total income",        f"{total_income:,.2f}")
        m2.metric("Total expenses",      f"{total_expense:,.2f}")
        m3.metric(
            "Net balance",
            f"{net:,.2f}",
            delta=f"{net:+,.2f}",
            delta_color="normal",
        )
        m4.metric("Transactions shown",  len(filtered_df))
    except Exception:
        pass

st.markdown("---")

# ── Transactions table ─────────────────────────────────────────────────────────
st.subheader("Transactions")

if "Bank Name" in filtered_df.columns:
    filtered_df["Bank Logo"] = filtered_df["Bank Name"].apply(get_bank_domain)

EXPECTED_COLS = [
    "Profile", "Date", "Bank Logo", "Bank Name",
    "Category", "Type", "Amount", "Has Proof",
]
display_cols = [c for c in EXPECTED_COLS if c in filtered_df.columns]

st.dataframe(
    filtered_df[display_cols],
    use_container_width=True,
    hide_index=True,
    column_config={
        "Date":      st.column_config.DateColumn("Date",     format="DD MMM YYYY"),
        "Amount":    st.column_config.NumberColumn("Amount", format="%.2f"),
        "Bank Logo": st.column_config.ImageColumn("Bank",    help="Logos by Clearbit"),
        "Has Proof": st.column_config.CheckboxColumn("Has proof"),
        "Type":      st.column_config.TextColumn("Type"),
    },
)

st.caption(f"Showing {len(filtered_df)} of {len(df)} transactions.")

# ── Delete transactions ────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("Manage transactions")

with st.expander("Delete transactions"):
    if "ID" not in filtered_df.columns:
        st.warning("Cannot delete: the `ID` column is missing from the database.")
    else:
        options_map = create_options_map(filtered_df)
        tx_ids      = filtered_df["ID"].astype(str).tolist()

        selected_ids = st.multiselect(
            "Select transactions to remove",
            options=tx_ids,
            format_func=lambda x: options_map.get(x, x),
            placeholder="Choose one or more transactions…",
        )

        if st.button("Delete selected", type="primary"):
            if not selected_ids:
                st.warning("Please select at least one transaction.")
            else:
                with st.spinner("Deleting…"):
                    if delete_transaction(selected_ids):
                        st.success(
                            f"{len(selected_ids)} transaction(s) deleted successfully."
                        )
                        st.rerun()
