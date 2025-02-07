# data_loader.py
import streamlit as st
import pandas as pd
from io import StringIO
from datetime import datetime

def load_data():
    st.sidebar.header("Upload Your Data")
    data_source = st.sidebar.radio("Data Source", ("CSV File", "Google Spreadsheet URL"))
    
    df = None
    if data_source == "CSV File":
        uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
            except Exception as e:
                st.error(f"Error loading CSV: {e}")
    else:
        sheet_url = st.sidebar.text_input("Enter Google Spreadsheet CSV URL")
        if sheet_url:
            try:
                df = pd.read_csv(sheet_url)
            except Exception as e:
                st.error(f"Error loading Google Spreadsheet: {e}")
    
    if df is not None:
        # Convert Year and Month to proper data types if necessary.
        if "Year" in df.columns and "Month" in df.columns:
            df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
            df["Month"] = pd.to_numeric(df["Month"], errors="coerce")
            # Create a combined date column
            df["Date"] = pd.to_datetime(df["Year"].astype(str) + "-" + df["Month"].astype(str) + "-01")
        return df
    else:
        st.warning("Please upload a CSV file or provide a valid Google Spreadsheet link.")
        return pd.DataFrame()  # return empty DataFrame if no data is loaded
