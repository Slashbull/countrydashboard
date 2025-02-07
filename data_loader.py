# data_loader.py
import streamlit as st
import pandas as pd
from io import StringIO
import requests
import config

def load_csv_data(uploaded_file) -> pd.DataFrame:
    """
    Load CSV data from an uploaded file with caching.
    
    Parameters:
        uploaded_file: An uploaded file object from Streamlit.
        
    Returns:
        A Pandas DataFrame containing the CSV data.
    """
    try:
        df = pd.read_csv(uploaded_file, low_memory=False)
    except Exception as e:
        st.error(f"🚨 Error processing CSV file: {e}")
        df = pd.DataFrame()
    return df

def upload_data() -> pd.DataFrame:
    """
    Handle data upload from either a CSV file or a Google Sheets link.
    Preprocesses the data by converting Year and Month columns to a datetime "Date" field.
    The data is then stored in session state for the duration of the session.
    
    Returns:
        A Pandas DataFrame containing the uploaded and processed data.
    """
    st.markdown("<h2 style='text-align: center;'>📂 Upload or Link Data</h2>", unsafe_allow_html=True)
    
    # If data is already uploaded, inform the user.
    if "uploaded_data" in st.session_state:
        st.info("Data is already loaded. Use 'Reset Data' from the sidebar to reload.")
        return st.session_state["uploaded_data"]
    
    upload_option = st.radio("📥 Choose Data Source:", ("Upload CSV", "Google Sheet Link"), index=0)
    df = None

    if upload_option == "Upload CSV":
        uploaded_file = st.file_uploader("Upload CSV File", type=["csv"],
                                         help="Upload your CSV file containing your data.")
        if uploaded_file is not None:
            df = load_csv_data(uploaded_file)
    else:
        # Use Google Sheet CSV export URL format
        sheet_url = st.text_input("🔗 Enter Google Sheet Link:")
        # Use a default sheet name from config, or default to "Sheet1"
        sheet_name = getattr(config, "DEFAULT_SHEET_NAME", "Sheet1")
        if sheet_url and st.button("Load Google Sheet"):
            try:
                # Extract the sheet ID from the URL
                sheet_id = sheet_url.split("/d/")[1].split("/")[0]
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
                response = requests.get(csv_url)
                response.raise_for_status()
                df = pd.read_csv(StringIO(response.text), low_memory=False)
            except Exception as e:
                st.error(f"🚨 Error loading Google Sheet: {e}")

    if df is not None and not df.empty:
        # Convert Year and Month to numeric (if available) and create a 'Date' column.
        if "Year" in df.columns and "Month" in df.columns:
            df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
            df["Month"] = pd.to_numeric(df["Month"], errors="coerce")
            # Combine Year and Month into a Date column (using the first day of the month)
            df["Date"] = pd.to_datetime(df["Year"].astype(str) + "-" + df["Month"].astype(str) + "-01")
        return df
    else:
        st.warning("No data loaded. Please upload a CSV file or provide a valid Google Spreadsheet link.")
        return pd.DataFrame()
