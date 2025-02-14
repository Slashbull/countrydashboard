# core_system.py
import streamlit as st
import pandas as pd
import requests
from io import StringIO
import logging
from datetime import datetime

# Additional library for advanced sidebar navigation
from streamlit_option_menu import option_menu

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

# -----------------------------------------------------------------------------
# Set page configuration as the very first Streamlit command
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Trade Data Dashboard", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Custom CSS for enhanced UI/UX
# -----------------------------------------------------------------------------
custom_css = """
<style>
/* Custom sidebar style */
.css-1d391kg {  
    background-color: #f0f2f6;
}
/* Custom header style */
.css-18e3th9 {
    font-family: 'Segoe UI', sans-serif;
    font-weight: bold;
    font-size: 1.5rem;
    color: #333;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------
log_level = getattr(logging, config.LOG_LEVEL, logging.INFO)
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=log_level)
logger = logging.getLogger(__name__)
logger.info("Core system starting with log level: %s", config.LOG_LEVEL)

# -----------------------------------------------------------------------------
# USER AUTHENTICATION & SESSION MANAGEMENT
# -----------------------------------------------------------------------------
def authenticate_user():
    """Display a login form in the sidebar and authenticate the user."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.sidebar.title("🔒 Login")
        username = st.sidebar.text_input("Username", key="username")
        password = st.sidebar.text_input("Password", type="password", key="password")
        if st.sidebar.button("Login"):
            if username == config.USERNAME and password == config.PASSWORD:
                st.session_state["authenticated"] = True
                logger.info("User %s authenticated successfully.", username)
                st.rerun()
            else:
                st.sidebar.error("🚨 Invalid credentials")
                logger.warning("Failed login attempt for username: %s", username)
        st.stop()

def logout_button():
    """Display a logout button that clears the session state."""
    if st.sidebar.button("🔓 Logout"):
        st.session_state.clear()
        logger.info("User logged out.")
        st.rerun()

# -----------------------------------------------------------------------------
# DATA LOADING AND PREPROCESSING FUNCTIONS
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=True, max_entries=config.CACHE_MAX_ENTRIES)
def load_csv(file) -> pd.DataFrame:
    """Load CSV data into a DataFrame with caching."""
    try:
        df = pd.read_csv(file, low_memory=False)
        logger.info("CSV file loaded successfully with %d records.", df.shape[0])
    except Exception as e:
        st.error(f"🚨 Error loading CSV: {e}")
        logger.error("Error in load_csv: %s", e)
        df = pd.DataFrame()
    return df

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert the 'Tons' column to numeric (removing commas if necessary) and create a
    'Period' column from 'Month' and 'Year'. Supports both numeric and abbreviated month values.
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
            logger.info("Period column created successfully.")
        except Exception as e:
            st.error("🚨 Error processing date fields. Check Month and Year formats.")
            logger.error("Error in preprocess_data (Period parsing): %s", e)
    return df.convert_dtypes()

def upload_data():
    """
    Display an upload widget to load data either from a CSV file or from a permanent
    Google Sheet link (if configured). Applies preprocessing and global filters.
    """
    st.markdown("<h2>📂 Upload or Link Trade Data</h2>", unsafe_allow_html=True)
    if "data" in st.session_state:
        st.info("Data already loaded.")
        return st.session_state["data"]

    df = None
    if config.USE_PERMANENT_GOOGLE_SHEET_LINK:
        sheet_url = config.PERMANENT_GOOGLE_SHEET_LINK
        st.info("Loading data from permanent Google Sheet...")
        try:
            sheet_id = sheet_url.split("/d/")[1].split("/")[0]
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={config.DEFAULT_SHEET_NAME}"
            response = requests.get(csv_url)
            response.raise_for_status()
            df = pd.read_csv(StringIO(response.text), low_memory=False)
            st.success("✅ Data loaded from permanent Google Sheet.")
            logger.info("Data loaded from Google Sheet.")
        except Exception as e:
            st.error(f"🚨 Error loading Google Sheet: {e}")
            logger.error("Error loading permanent Google Sheet: %s", e)
    else:
        option = st.radio("Choose Data Source:", ("Upload CSV", "Google Sheet Link"))
        if option == "Upload CSV":
            file = st.file_uploader("Upload CSV File", type=["csv"], help="Upload your trade data CSV.")
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
                    logger.info("Data loaded from user-specified Google Sheet.")
                except Exception as e:
                    st.error(f"🚨 Error loading Google Sheet: {e}")
                    logger.error("Error loading user-provided Google Sheet: %s", e)
    if df is not None and not df.empty:
        df = preprocess_data(df)
        st.session_state["data"] = df
        filtered_df, _ = apply_filters(df)
        st.session_state["filtered_data"] = filtered_df
        st.success("✅ Data loaded and preprocessed successfully!")
        logger.info("Data preprocessed and filters applied.")
    else:
        st.info("No data loaded yet. Please upload or link a data source.")
    return df

def reset_data():
    """Clear the loaded data and re-run the app."""
    if st.sidebar.button("Reset Data", key="reset_data"):
        st.session_state.pop("data", None)
        st.session_state.pop("filtered_data", None)
        logger.info("Data reset by user.")
        st.rerun()

def reset_filters():
    """
    Clear all filter selections stored in session_state.
    This function assumes filter widgets have keys that start with "multiselect_".
    """
    filter_keys = [key for key in st.session_state.keys() if key.startswith("multiselect_")]
    for key in filter_keys:
        del st.session_state[key]
    logger.info("Filters reset by user.")
    st.rerun()

def get_current_data():
    """Return filtered data if available; otherwise, return raw uploaded data."""
    return st.session_state.get("filtered_data", st.session_state.get("data"))

def display_footer():
    """Display a footer at the bottom of the app."""
    footer_html = """
    <div style="text-align: center; padding: 10px; color: #666;">
      © 2025 TradeDataDashboard. All rights reserved.
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MAIN APPLICATION FUNCTION
# -----------------------------------------------------------------------------
def main():
    # Authentication & Logout
    authenticate_user()
    logout_button()
    
    # Advanced Sidebar Navigation using streamlit-option-menu
    with st.sidebar:
        selected_page = option_menu(
            "Navigation", 
            options=[
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
            ],
            icons=[
                "house", "bar-chart-line", "search", "bell", "graph-up", 
                "geo-alt", "layers", "diagram-3", "clock", "calendar", 
                "cloud-sun", "kanban", "file-earmark"
            ],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {"padding": "5!important", "background-color": "#f0f2f6"},
                "icon": {"color": "orange", "font-size": "18px"}, 
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
                "nav-link-selected": {"background-color": "#02ab21"},
            }
        )
        # Additional buttons in the sidebar for resetting data and filters.
        if st.button("Reset Filters", key="reset_filters"):
            reset_filters()
        if "data" in st.session_state and "Period_dt" in st.session_state["data"].columns:
            last_updated = st.session_state["data"]["Period_dt"].max().strftime("%b-%Y")
            st.info(f"Data Last Updated: {last_updated}")
    st.session_state["page"] = selected_page

    # Data reset button always available in sidebar.
    reset_data()

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
    main()
