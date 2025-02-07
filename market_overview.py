# core_system.py (Final Version)
import streamlit as st
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
from scenario_simulation import simulate_scenario  # Optional
from reporting import generate_report              # Optional

st.set_page_config(page_title=config.APP_TITLE, layout="wide")
st.title(config.APP_TITLE)

# Authentication
if not login():
    st.stop()

# Data Upload & Storage
if "uploaded_data" not in st.session_state or st.sidebar.button("Reset Data"):
    df = upload_data()
    st.session_state["uploaded_data"] = df
else:
    df = st.session_state["uploaded_data"]

if df.empty:
    st.warning("No data loaded. Please upload your CSV or provide a Google Sheet link.")
    st.stop()

# Dashboard Navigation
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

if simulate_scenario is not None:
    dashboard_options.append("Scenario Simulation")
if generate_report is not None:
    dashboard_options.append("Reporting")

selection = st.sidebar.radio("Select Dashboard", dashboard_options)

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
elif selection == "Scenario Simulation":
    simulate_scenario(df)
elif selection == "Reporting":
    generate_report(df)
