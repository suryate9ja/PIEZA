import streamlit as st
import pandas as pd
import json
import google.generativeai as genai

from utils import show_global_sidebar, fetch_transactions

st.set_page_config(page_title="AI Advisor - PIEZA", layout="wide")
show_global_sidebar()

st.title("AI Financial Advisor")
st.markdown(
    "Select a time period and let Gemini analyse your transactions to suggest "
    "spending reductions and faster loan-clearing strategies."
)

if not st.session_state.gemini_api_key:
    st.warning("Configure your Gemini API Key in the sidebar to enable this page.")
    st.stop()

# ── Fetch data ─────────────────────────────────────────────────────────────────
df = fetch_transactions()

if df.empty:
    st.info("No transactions found. Add data on the Data Entry page first.")
    st.stop()

# ── Date range selector ────────────────────────────────────────────────────────
st.subheader("Analysis Period")

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
    st.error("Start date must be before end date.")
    st.stop()

# ── Quick summary of selected period ──────────────────────────────────────────
period_df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)].copy()

if period_df.empty:
    st.warning("No transactions in this period. Adjust the date range.")
    st.stop()

try:
    period_df["Amount"] = pd.to_numeric(period_df["Amount"], errors="coerce").fillna(0)
    income = period_df.loc[period_df["Type"] == "Income", "Amount"].sum()
    expense = period_df.loc[period_df["Type"] == "Expense", "Amount"].sum()

    m1, m2, m3 = st.columns(3)
    m1.metric("Period Income", f"{income:,.2f}")
    m2.metric("Period Expenses", f"{expense:,.2f}")
    m3.metric("Transactions", len(period_df))
except Exception:
    pass

st.markdown("---")

# ── Analyse button ─────────────────────────────────────────────────────────────
if st.button("Analyse Period", type="primary"):
    with st.spinner("Analysing your finances..."):
        try:
            genai.configure(api_key=st.session_state.gemini_api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")

            analysis_cols = [c for c in ["Date", "Profile", "Type", "Category", "Amount", "Bank Name"] if c in period_df.columns]
            payload = period_df[analysis_cols].to_dict(orient="records")

            # Keep payload size reasonable — send at most 200 rows
            if len(payload) > 200:
                payload = payload[:200]
                st.caption("Note: Analysis limited to the first 200 transactions in this period.")

            prompt = f"""
You are a strict, expert AI Financial Advisor. Your tone is professional and direct.

Analyse the following family transaction data covering {start_date} to {end_date}.

Provide your response in this exact structure (use markdown headings, no emojis):

## Summary
A 3-4 sentence overview of income vs expenses and overall financial health.

## Spending Analysis
Identify the top 3 expense categories. For each, explain if the spending level is concerning and why.

## Recommendations to Reduce Spending
Give 3-5 specific, actionable suggestions based on the actual data.

## Loan and EMI Strategy
Based on the income-to-expense ratio, suggest a concrete strategy for clearing loans or EMIs faster (e.g. avalanche method, surplus allocation).

## Monthly Target
Suggest a realistic monthly savings target in the same currency as the data.

Transaction data (JSON):
{json.dumps(payload, indent=2, default=str)}
"""

            response = model.generate_content(prompt)
            st.markdown("### AI Analysis")
            st.markdown(response.text)

        except Exception as e:
            st.error(f"Gemini API error: {e}")
