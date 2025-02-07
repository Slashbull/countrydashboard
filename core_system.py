# core_system.py
import streamlit as st
from config import APP_TITLE
from authentication import login

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

st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)

# Perform authentication; if unsuccessful, stop the app.
if not login():
    st.stop()

# Sidebar for dashboard navigation
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
