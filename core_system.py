import streamlit as st
import pandas as pd
import requests
from io import StringIO
import logging
from datetime import datetime

# Import configuration and filters
import config
from filters import apply_filters

# Import dashboard modules (only those we are using)
from market_overview import market_overview_dashboard
from Alerts_Forcasting import alerts_forecasting_dashboard
from country_level_insights import country_level_insights_dashboard
from time_series_decomposition import time_series_decomposition_dashboard
from reporting import reporting_dashboard

# -----------------------------------------------------------------------------
# Set page configuration (must be the first Streamlit command)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Trade Data Dashboard", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Setup basic logging
# -----------------------------------------------------------------------------
log_level = getattr(logging, config.LOG_LEVEL, logging.INFO)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=log_level)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# USER AUTHENTICATION
# -----------------------------------------------------------------------------
def authenticate_user():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        st.sidebar.title("Login")
        username = st.sidebar.text_input("Username", key="username")
        password = st.sidebar.text_input("Password", type="password", key="password")
        if st.sidebar.button("Login"):
            if username == config.USERNAME and password == config.PASSWORD:
                st.session_state["authenticated"] = True
                logger.info("User %s authenticated", username)
                st.rerun()
            else:
                st.sidebar.error("Invalid credentials")
        st.stop()

def logout_button():
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

# -----------------------------------------------------------------------------
# DATA LOADING & PREPROCESSING
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=True, max_entries=config.CACHE_MAX_ENTRIES)
def load_csv(file) -> pd.DataFrame:
    try:
        df = pd.read_csv(file, low_memory=False)
        logger.info("CSV loaded with %d rows", df.shape[0])
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        logger.error("Error loading CSV: %s", e)
        return pd.DataFrame()

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    if "Tons" in df.columns:
        df["Tons"] = pd.to_numeric(df["Tons"].astype(str).str.replace(",", "", regex=False), errors="coerce")
    if "Year" in df.columns and "Month" in df.columns:
        try:
            def parse_period(row):
                m = row["Month"]
                y = str(row["Year"])
                if str(m).isdigit():
                    return datetime.strptime(f"{int(m)} {y}", "%m %Y")
                else:
                    return datetime.strptime(f"{m} {y}", "%b %Y")
            df["Period_dt"] = df.apply(parse_period, axis=1)
            sorted_periods = sorted(df["Period_dt"].dropna().unique())
            period_labels = [dt.strftime("%b-%Y") for dt in sorted_periods]
            df["Period"] = df["Period_dt"].dt.strftime("%b-%Y")
            df["Period"] = pd.Categorical(df["Period"], categories=period_labels, ordered=True)
        except Exception as e:
            st.error("Error processing date fields.")
            logger.error("Date processing error: %s", e)
    return df.convert_dtypes()

def upload_data():
    st.markdown("## Upload or Link Trade Data")
    if "data" in st.session_state:
        st.info("Data already loaded.")
        return st.session_state["data"]
    df = None
    if config.USE_PERMANENT_GOOGLE_SHEET_LINK:
        try:
            sheet_url = config.PERMANENT_GOOGLE_SHEET_LINK
            sheet_id = sheet_url.split("/d/")[1].split("/")[0]
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={config.DEFAULT_SHEET_NAME}"
            response = requests.get(csv_url)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text), low_memory=False)
            st.success("Data loaded from permanent Google Sheet.")
        except Exception as e:
            st.error(f"Error loading Google Sheet: {e}")
    else:
        option = st.radio("Data Source:", ("Upload CSV", "Google Sheet Link"))
        if option == "Upload CSV":
            file = st.file_uploader("Upload CSV", type=["csv"])
            if file:
                df = load_csv(file)
        else:
            sheet_url = st.text_input("Enter Google Sheet URL:")
            if sheet_url and st.button("Load Google Sheet"):
                try:
                    sheet_id = sheet_url.split("/d/")[1].split("/")[0]
                    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={config.DEFAULT_SHEET_NAME}"
                    response = requests.get(csv_url)
                    response.raise_for_status()
                    df = pd.read_csv(StringIO(response.text), low_memory=False)
                except Exception as e:
                    st.error(f"Error loading Google Sheet: {e}")
    if df is not None and not df.empty:
        df = preprocess_data(df)
        st.session_state["data"] = df
        filtered_df, _ = apply_filters(df)
        st.session_state["filtered_data"] = filtered_df
        st.success("Data loaded and preprocessed.")
    else:
        st.info("No data loaded yet.")
    return df

def reset_data():
    if st.sidebar.button("Reset Data"):
        st.session_state.pop("data", None)
        st.session_state.pop("filtered_data", None)
        st.rerun()

def reset_filters():
    for key in list(st.session_state.keys()):
        if key.startswith("multiselect_"):
            st.session_state[key] = []
    st.rerun()

def get_current_data():
    return st.session_state.get("filtered_data", st.session_state.get("data"))

def display_footer():
    st.markdown("<div style='text-align:center; padding:10px; color:#666;'>© 2025 TradeDataDashboard. All rights reserved.</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MAIN FUNCTION
# -----------------------------------------------------------------------------
def main():
    authenticate_user()
    logout_button()
    
    # Navigation options based on your final structure.
    nav_options = [
        "Home", 
        "Market Overview", 
        "Alerts_Forcasting", 
        "Country-Level Insights", 
        "Time Series Decomposition", 
        "Reporting"
    ]
    selected_page = st.sidebar.radio("Navigation", nav_options)
    
    st.sidebar.button("Reset Filters", on_click=reset_filters)
    st.session_state["page"] = selected_page
    reset_data()

    if selected_page == "Home":
        st.header("Executive Summary & Data Upload")
        df = upload_data()
        if df is not None and not df.empty:
            st.sidebar.download_button(
                "Download Processed Data", 
                df.to_csv(index=False).encode("utf-8"), 
                "processed_data.csv", 
                "text/csv"
            )
    else:
        df = get_current_data()
        if df is None or df.empty:
            st.error("No data available. Please upload data on the Home page.")
        else:
            filtered_df, _ = apply_filters(df)
            if selected_page == "Market Overview":
                market_overview_dashboard(filtered_df)
            elif selected_page == "Alerts_Forcasting":
                alerts_forecasting_dashboard(filtered_df)
            elif selected_page == "Country-Level Insights":
                country_level_insights_dashboard(filtered_df)
            elif selected_page == "Time Series Decomposition":
                time_series_decomposition_dashboard(filtered_df)
            elif selected_page == "Reporting":
                reporting_dashboard(filtered_df)
    
    display_footer()

if __name__ == "__main__":
    main()
