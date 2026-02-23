import streamlit as st
import pandas as pd
from utils import show_global_sidebar, fetch_transactions
import google.generativeai as genai
import json

# Page config
st.set_page_config(page_title="AI Advisor - PIEZA", layout="wide")

# Show sidebar
show_global_sidebar()

st.title("AI Financial Advisor")
st.markdown("Get personalized recommendations on reducing spending and clearing loans based on your recent transactions.")

if not st.session_state.gemini_api_key:
    st.warning("Please configure your Gemini API Key in the sidebar to enable the AI Advisor.")
else:
    # Fetch from DB
    df = fetch_transactions()
    
    if df.empty:
        st.info("No transactions found to analyze. Please add some data on the Data Entry page.")
    else:
        # Date filtering
        st.subheader("Select Analysis Period")
        
        # Convert string dates
        try:
            df['Date'] = pd.to_datetime(df['Date']).dt.date
            min_date = df['Date'].min()
            max_date = df['Date'].max()
        except:
            min_date = pd.to_datetime('today').date()
            max_date = pd.to_datetime('today').date()
            
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", min_date)
        with col2:
            end_date = st.date_input("End Date", max_date)
            
        analyze_button = st.button("Analyze Period", type="primary")
        
        if analyze_button:
            # Filter the dataframe
            filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
            
            if filtered_df.empty:
                st.warning("No transactions found in this period to analyze.")
            else:
                with st.spinner("Analyzing your spending and loan strategy..."):
                    try:
                        genai.configure(api_key=st.session_state.gemini_api_key)
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        
                        # Prepare data for API
                        # Ensure we don't pass massive DFs to the prompt directly to avoid token limits
                        # Just select necessary columns
                        analysis_cols = ["Date", "Profile", "Type", "Category", "Amount", "Bank Name"]
                        analysis_cols = [c for c in analysis_cols if c in filtered_df.columns]
                        
                        analysis_data = filtered_df[analysis_cols].to_dict(orient="records")
                        
                        prompt = f"""
                        You are a strict, expert AI Financial Advisor.
                        
                        Analyze the following transaction data for the period {start_date} to {end_date}.
                        The data is provided in JSON format.
                        
                        Your goal is to provide specific suggestions on:
                        1. Reducing unnecessary spending, identifying any problem categories.
                        2. Ideas and strategies for clearing loans/EMIs faster based on their income vs. expense ratio.
                        
                        Format your response professionally and clearly using standard markdown (no emojis).
                        
                        Data:
                        {json.dumps(analysis_data, indent=2, default=str)}
                        """
                        
                        response = model.generate_content(prompt)
                        
                        st.markdown("### AI Analysis Results")
                        st.markdown(response.text)
                        
                    except Exception as e:
                        st.error(f"An error occurred while communicating with Gemini API: {e}")
