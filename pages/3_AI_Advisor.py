import streamlit as st
import pandas as pd
import json
import google.generativeai as genai

from utils import show_global_sidebar, fetch_transactions, apply_custom_css

st.set_page_config(page_title="AI Advisor - PIEZA", layout="wide", page_icon="🤖")
apply_custom_css()
show_global_sidebar()

st.title("🤖 AI Financial Advisor")
st.markdown(
    "Select a time period and let Gemini analyze your transactions to suggest "
    "spending reductions and faster loan-clearing strategies."
)

if not st.session_state.get("gemini_api_key"):
    st.warning(
        "Configure your **Gemini API Key** in the sidebar to enable this page.",
        icon="🔑",
    )
    st.stop()

# ── Fetch data ─────────────────────────────────────────────────────────────────
df = fetch_transactions()

if df.empty:
    st.info(
        "No transactions found. Add data on the **Data Entry** page first.",
        icon="ℹ️",
    )
    st.stop()

# ── Date range selector ────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📅 Analysis Period")

try:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
    df = df.dropna(subset=["Date"])
    min_date = df["Date"].min()
    max_date = df["Date"].max()
except Exception:
    min_date = max_date = pd.Timestamp.today().date()

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=min_date)
with col2:
    end_date = st.date_input("End Date", value=max_date)

if start_date > end_date:
    st.error("Start date must be before the end date.")
    st.stop()

# Guard: the Date column must exist after parsing (it could be missing if the
# sheet has rows but incorrect headers).
if "Date" not in df.columns:
    st.error(
        "The 'Date' column is missing from your data. "
        "Please ensure Row 1 of PIEZA_DB has the correct headers: "
        "ID | Profile | Date | Type | Category | Amount | Bank Name | Has Proof"
    )
    st.stop()

# ── Period summary metrics ─────────────────────────────────────────────────────
period_df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)].copy()

if period_df.empty:
    st.warning(
        "No transactions found in this period. Adjust the date range and try again.",
        icon="⚠️",
    )
    st.stop()

st.markdown("---")
st.subheader("📊 Period Summary")

try:
    period_df["Amount"] = pd.to_numeric(
        period_df["Amount"], errors="coerce"
    ).fillna(0)
    income = period_df.loc[period_df["Type"] == "Income", "Amount"].sum()
    expense = period_df.loc[period_df["Type"] == "Expense", "Amount"].sum()
    net = income - expense

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Period Income", f"{income:,.2f}")
    m2.metric("Period Expenses", f"{expense:,.2f}")
    m3.metric("Net Balance", f"{net:,.2f}", delta=f"{net:,.2f}", delta_color="normal")
    m4.metric("Transactions", len(period_df))
except Exception:
    pass

# ── Analyze button ─────────────────────────────────────────────────────────────
st.markdown("---")

if st.button("🔍 Analyze Period", type="primary"):
    with st.spinner("Analyzing your finances with Gemini…"):
        try:
            genai.configure(api_key=st.session_state.gemini_api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")

            analysis_cols = [
                c
                for c in [
                    "Date",
                    "Profile",
                    "Type",
                    "Category",
                    "Amount",
                    "Bank Name",
                ]
                if c in period_df.columns
            ]
            payload = period_df[analysis_cols].to_dict(orient="records")

            # Keep payload size reasonable — send at most 200 rows.
            if len(payload) > 200:
                payload = payload[:200]
                st.caption(
                    "Note: Analysis is limited to the first 200 transactions in this period."
                )

            prompt = f"""
You are a strict, expert AI Financial Advisor. Your tone is professional and direct.

Analyze the following family transaction data covering {start_date} to {end_date}.

Provide your response in this exact structure (use markdown headings, no emojis):

## Summary
A 3-4 sentence overview of income vs. expenses and overall financial health.

## Spending Analysis
Identify the top 3 expense categories. For each, explain if the spending level is
concerning and why.

## Recommendations to Reduce Spending
Give 3-5 specific, actionable suggestions based on the actual data.

## Loan and EMI Strategy
Based on the income-to-expense ratio, suggest a concrete strategy for clearing loans
or EMIs faster (e.g., the avalanche method or surplus allocation).

## Monthly Savings Target
Suggest a realistic monthly savings target in the same currency as the data.

Transaction data (JSON):
{json.dumps(payload, indent=2, default=str)}
"""

            response = model.generate_content(prompt)

            st.markdown("---")
            st.subheader("📈 AI Analysis")
            st.markdown(response.text)

        except Exception as e:
            st.error(f"Gemini API error: {e}")
