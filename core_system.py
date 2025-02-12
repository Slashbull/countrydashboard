# core_system.py
import streamlit as st
import pandas as pd
import requests
from io import StringIO
import logging
from datetime import datetime

# Import configuration and filters
import config
from filters import apply_filters

# Import dashboard modules
from market_overview import market_overview_dashboard
from detailed_analysis import detailed_analysis_dashboard
from ai_based_alerts import ai_based_alerts_dashboard
from forecasting import forecasting_dashboard
from country_level_insights import country_level_insights_dashboard
from segmentation_analysis import segmentation_analysis_dashboard
from correlation_analysis import correlation_analysis_dashboard
from time_series_decomposition import time_series_decomposition_dashboard
from calendar_insights import calendar_insights_dashboard
from climate_insights import climate_insights_dashboard
from scenario_simulation import scenario_simulation_dashboard
from reporting import reporting_dashboard

# Configure logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def authenticate_user():
    """Display a login form in the sidebar and authenticate the user."""
    st.session_state.setdefault("authenticated", False)
    if not st.session_state["authenticated"]:
        st.sidebar.title("🔒 Login")
        username = st.sidebar.text_input("Username", key="username")
        password = st.sidebar.text_input("Password", type="password", key="password")
        if st.sidebar.button("Login"):
            if username == config.USERNAME and password == config.PASSWORD:
                st.session_state["authenticated"] = True
                st.experimental_rerun()
            else:
                st.sidebar.error("🚨 Invalid credentials")
        st.stop()

def logout_button():
    """Display a logout button that clears the session."""
    if st.sidebar.button("🔓 Logout"):
        st.session_state.clear()
        st.experimental_rerun()

@st.cache_data(show_spinner=False)
def load_csv(file) -> pd.DataFrame:
    """Load CSV data into a DataFrame with caching."""
    try:
        df = pd.read_csv(file, low_memory=False)
    except Exception as e:
        st.error(f"🚨 Error loading CSV: {e}")
        logger.error("Error in load_csv: %s", e)
        df = pd.DataFrame()
    return df

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert the 'Tons' column to numeric and create a 'Period' column from Month and Year.
    If Month is numeric, it is parsed as a month number; otherwise, as an abbreviated month.
    """
    if "Tons" in df.columns:
        df["Tons"] = pd.to_numeric(
            df["Tons"].astype(str).str.replace(",", "", regex=False),
            errors="coerce"
        )
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
            st.error("🚨 Error processing date fields. Check Month and Year formats.")
            logger.error("Date parsing error: %s", e)
    return df.convert_dtypes()

def upload_data():
    """
    Handle data ingestion:
      - If a Google Sheet link is defined in config, load data automatically.
      - Otherwise, prompt the user to either upload a CSV file or provide a Google Sheet link.
      - Preprocess and cache the data in session state.
    """
    st.markdown("<h2 style='text-align: center;'>📂 Upload or Link Trade Data</h2>", unsafe_allow_html=True)
    
    if "data" in st.session_state:
        st.info("Data already loaded.")
        return st.session_state["data"]

    df = None
    # Auto-load from Google Sheet if configured.
    if config.GOOGLE_SHEET_LINK:
        st.info("Loading data from the configured Google Sheet...")
        sheet_url = config.GOOGLE_SHEET_LINK
        sheet_name = config.DEFAULT_SHEET_NAME
        try:
            sheet_id = sheet_url.split("/d/")[1].split("/")[0]
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
            response = requests.get(csv_url)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text), low_memory=False)
            st.success("✅ Google Sheet loaded successfully from configuration.")
        except Exception as e:
            st.error(f"🚨 Error loading Google Sheet from config: {e}")
            logger.error("Error loading Google Sheet from config: %s", e)
    
    if df is None:
        upload_option = st.radio("📥 Choose Data Source:", ("Upload CSV", "Google Sheet Link"), index=0)
        if upload_option == "Upload CSV":
            file = st.file_uploader("Upload CSV File", type=["csv"], help="Upload your trade data CSV.")
            if file:
                df = load_csv(file)
        else:
            sheet_url = st.text_input("🔗 Enter Google Sheet Link:")
            sheet_name = config.DEFAULT_SHEET_NAME
            if sheet_url and st.button("Load Google Sheet"):
                try:
                    sheet_id = sheet_url.split("/d/")[1].split("/")[0]
                    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
                    response = requests.get(csv_url)
                    response.raise_for_status()
                    df = pd.read_csv(StringIO(response.text), low_memory=False)
                except Exception as e:
                    st.error(f"🚨 Error loading Google Sheet: {e}")
                    logger.error("Error loading Google Sheet: %s", e)
    
    if df is not None and not df.empty:
        df = preprocess_data(df)
        st.session_state["data"] = df
        st.sidebar.header("Filters")
        filtered_df, _ = apply_filters(df)
        st.session_state["filtered_data"] = filtered_df
        st.success("✅ Data loaded and filtered successfully!")
        logger.info("Data loaded.")
    else:
        st.info("No data loaded yet. Please upload a file or provide a valid Google Sheet link.")
    return df

def reset_data():
    """Remove data from session state and rerun the app."""
    if st.sidebar.button("Reset Data", key="reset_data"):
        st.session_state.pop("data", None)
        st.session_state.pop("filtered_data", None)
        st.experimental_rerun()

def get_current_data():
    """Return filtered data if available; otherwise, return raw uploaded data."""
    return st.session_state.get("filtered_data", st.session_state.get("data"))

def display_footer():
    """Display a simple footer."""
    footer_html = """
    <div style="text-align: center; padding: 10px; color: #666;">
        © 2025 TradeDataDashboard. All rights reserved.
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title="Trade Data Dashboard", layout="wide", initial_sidebar_state="expanded")
    
    # Sidebar Navigation
    pages = [
        "Home",
        "Market Overview",
        "Detailed Analysis",
        "AI-Based Alerts",
        "Forecasting",
        "Country-Level Insights",
        "Segmentation Analysis",
        "Correlation Analysis",
        "Time Series Decomposition",
        "Calendar Insights",
        "Climate Insights",
        "Scenario Simulation",
        "Reporting"
    ]
    selected_page = st.sidebar.radio("Navigation", pages, index=0)
    st.session_state["page"] = selected_page

    # Data upload and reset buttons.
    if selected_page == "Home":
        st.header("Executive Summary & Data Upload")
        df = upload_data()
        if df is not None and not df.empty:
            st.sidebar.download_button(
                "📥 Download Processed Data",
                df.to_csv(index=False).encode("utf-8"),
                "processed_data.csv",
                "text/csv"
            )
    else:
        df = get_current_data()
        if df is None or df.empty:
            st.error("No data available. Please upload data on the Home page.")
        else:
            # Reapply global filters.
            filtered_df, _ = apply_filters(df)
            if selected_page == "Market Overview":
                market_overview_dashboard(filtered_df)
            elif selected_page == "Detailed Analysis":
                detailed_analysis_dashboard(filtered_df)
            elif selected_page == "AI-Based Alerts":
                ai_based_alerts_dashboard(filtered_df)
            elif selected_page == "Forecasting":
                forecasting_dashboard(filtered_df)
            elif selected_page == "Country-Level Insights":
                country_level_insights_dashboard(filtered_df)
            elif selected_page == "Segmentation Analysis":
                segmentation_analysis_dashboard(filtered_df)
            elif selected_page == "Correlation Analysis":
                correlation_analysis_dashboard(filtered_df)
            elif selected_page == "Time Series Decomposition":
                time_series_decomposition_dashboard(filtered_df)
            elif selected_page == "Calendar Insights":
                calendar_insights_dashboard(filtered_df)
            elif selected_page == "Climate Insights":
                climate_insights_dashboard(filtered_df)
            elif selected_page == "Scenario Simulation":
                scenario_simulation_dashboard(filtered_df)
            elif selected_page == "Reporting":
                reporting_dashboard(filtered_df)
    
    display_footer()

if __name__ == "__main__":
    authenticate_user()
    logout_button()
    main()
