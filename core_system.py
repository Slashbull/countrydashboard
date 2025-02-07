# core_system.py
import streamlit as st
import pandas as pd
import altair as alt
import requests
from io import StringIO
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.cluster import KMeans
import config

# -------------------------
# CONFIGURATION & UI SETUP
# -------------------------
APP_TITLE = config.APP_TITLE
CREDENTIALS = config.SINGLE_USER
DEFAULT_SHEET_NAME = config.DEFAULT_SHEET_NAME
OPEN_METEO_API_URL = config.OPEN_METEO_API_URL

st.set_page_config(page_title=APP_TITLE, layout="wide")
st.markdown(
    """
    <style>
    .main {font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;}
    .sidebar .sidebar-content {background-color: #f5f5f5; padding: 10px;}
    </style>
    """,
    unsafe_allow_html=True
)
st.title(APP_TITLE)

# -------------------------
# INLINE AUTHENTICATION
# -------------------------
def authenticate():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)
        username = st.text_input("Username", key="username")
        password = st.text_input("Password", type="password", key="password")
        if st.button("Login"):
            if username == CREDENTIALS["username"] and password == CREDENTIALS["password"]:
                st.success(f"Welcome, {CREDENTIALS['name']}!")
                st.session_state.logged_in = True
            else:
                st.error("🚨 Incorrect username or password.")
    return st.session_state.logged_in

if not authenticate():
    st.stop()

# -------------------------
# INLINE DATA UPLOAD
# -------------------------
def load_csv_data(uploaded_file) -> pd.DataFrame:
    try:
        df = pd.read_csv(uploaded_file, low_memory=False)
    except Exception as e:
        st.error(f"🚨 Error processing CSV file: {e}")
        df = pd.DataFrame()
    return df

def upload_data() -> pd.DataFrame:
    st.markdown("<h2 style='text-align: center;'>📂 Upload or Link Data</h2>", unsafe_allow_html=True)
    source = st.radio("Choose Data Source:", ("Upload CSV", "Google Sheet Link"), index=0)
    df = None
    if source == "Upload CSV":
        file = st.file_uploader("Upload CSV", type=["csv"], help="Upload your CSV file with trade data.")
        if file is not None:
            df = load_csv_data(file)
    else:
        sheet_url = st.text_input("Enter Google Sheet Link:")
        if sheet_url and st.button("Load Google Sheet"):
            try:
                sheet_id = sheet_url.split("/d/")[1].split("/")[0]
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={DEFAULT_SHEET_NAME}"
                response = requests.get(csv_url)
                response.raise_for_status()
                df = pd.read_csv(StringIO(response.text), low_memory=False)
            except Exception as e:
                st.error(f"🚨 Error loading Google Sheet: {e}")
    if df is not None and not df.empty:
        if "Year" in df.columns and "Month" in df.columns:
            df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
            df["Month"] = pd.to_numeric(df["Month"], errors="coerce")
            df["Date"] = pd.to_datetime(df["Year"].astype(str) + "-" + df["Month"].astype(str) + "-01")
        return df
    else:
        st.warning("No data loaded. Please upload a CSV file or provide a valid Google Sheet link.")
        return pd.DataFrame()

if "data" not in st.session_state or st.sidebar.button("Reset Data"):
    data = upload_data()
    st.session_state["data"] = data
else:
    data = st.session_state["data"]

if data.empty:
    st.warning("No data available.")
    st.stop()
else:
    st.write("Data loaded successfully! Preview:")
    st.dataframe(data.head())

# -------------------------
# IMPORT DASHBOARD MODULES
# -------------------------
from filters import add_filters
from market_overview import show_market_overview
from detailed_analysis import show_detailed_analysis
from ai_based_alerts import show_ai_based_alerts
from forecasting import show_forecasting
from country_level_insights import show_country_level_insights
from segmentation_analysis import show_segmentation_analysis
from correlation_analysis import show_correlation_analysis
from time_series_decomposition import show_time_series_decomposition
from calendar_insights import show_calendar_insights
from climate_insights import show_climate_insights
from scenario_simulation import simulate_scenario   # Optional
from reporting import generate_report                # Optional

# -------------------------
# MAIN NAVIGATION
# -------------------------
dashboards = [
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
choice = st.sidebar.radio("Select Dashboard", dashboards)

if choice == "Market Overview":
    show_market_overview()
elif choice == "Detailed Analysis":
    show_detailed_analysis()
elif choice == "AI-Based Alerts":
    show_ai_based_alerts()
elif choice == "Forecasting":
    show_forecasting()
elif choice == "Country-Level Insights":
    show_country_level_insights()
elif choice == "Segmentation Analysis":
    show_segmentation_analysis()
elif choice == "Correlation Analysis":
    show_correlation_analysis()
elif choice == "Time Series Decomposition":
    show_time_series_decomposition()
elif choice == "Calendar Insights":
    show_calendar_insights()
elif choice == "Climate Insights":
    show_climate_insights()
elif choice == "Scenario Simulation":
    simulate_scenario()
elif choice == "Reporting":
    generate_report()
