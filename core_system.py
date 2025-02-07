# core_system.py
import streamlit as st
import logging
import config
from authentication import login
from data_loader import upload_data

# Import dashboard modules
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

# Optional modules for additional features
try:
    from scenario_simulation import simulate_scenario
except ImportError:
    simulate_scenario = None

try:
    from reporting import generate_report
except ImportError:
    generate_report = None

# Set up basic logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Set page configuration
st.set_page_config(page_title=config.APP_TITLE, layout="wide")
st.title(config.APP_TITLE)

# ------------------------
# 1. Authentication
# ------------------------
if not login():
    st.stop()

# ------------------------
# 2. Data Upload and Storage in Session State
# ------------------------
if "uploaded_data" not in st.session_state or st.sidebar.button("Reset Data"):
    df = upload_data()
    st.session_state["uploaded_data"] = df
else:
    df = st.session_state["uploaded_data"]

if df.empty:
    st.warning("No data loaded. Please upload a CSV file or provide a Google Spreadsheet link.")
    st.stop()

# ------------------------
# 3. Dashboard Navigation
# ------------------------
dashboard_options = [
    "Market Overview",
    "Detailed Analysis",
    "AI-Based Alerts",
    "Forecasting",
    "Country-Level Insights",
    "Segmentation Analysis",
    "Correlation Analysis",
    "Time Series Decomposition",
    "Calendar Insights",
    "Climate Insights"
]

# Optionally include Scenario Simulation and Reporting if available.
if simulate_scenario is not None:
    dashboard_options.append("Scenario Simulation")
if generate_report is not None:
    dashboard_options.append("Reporting")

selection = st.sidebar.radio("Select Dashboard", dashboard_options)

# ------------------------
# 4. Route to the Selected Dashboard
# ------------------------
if selection == "Market Overview":
    show_market_overview()
elif selection == "Detailed Analysis":
    show_detailed_analysis()
elif selection == "AI-Based Alerts":
    show_ai_based_alerts()
elif selection == "Forecasting":
    show_forecasting()
elif selection == "Country-Level Insights":
    show_country_level_insights()
elif selection == "Segmentation Analysis":
    show_segmentation_analysis()
elif selection == "Correlation Analysis":
    show_correlation_analysis()
elif selection == "Time Series Decomposition":
    show_time_series_decomposition()
elif selection == "Calendar Insights":
    show_calendar_insights()
elif selection == "Climate Insights":
    show_climate_insights()
elif selection == "Scenario Simulation" and simulate_scenario is not None:
    simulate_scenario(df)  # Pass the loaded data
elif selection == "Reporting" and generate_report is not None:
    generate_report(df)  # Pass the loaded data
