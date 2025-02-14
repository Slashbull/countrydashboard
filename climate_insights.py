# climate_insights.py
import streamlit as st
import pandas as pd
import plotly.express as px
import requests

def climate_insights_dashboard():
    st.title("🌦 Climate Insights Dashboard")
    st.markdown("""
    This dashboard fetches a 7‑day weather forecast using the free Open‑Meteo API.  
    Enter the latitude and longitude to view the forecast for that location.
    """)

    # Input for location (default set to New Delhi, India)
    latitude = st.number_input("Enter Latitude", value=28.6139, format="%.4f")
    longitude = st.number_input("Enter Longitude", value=77.2090, format="%.4f")

    # Build API request URL for a 7-day forecast including max/min temperature and precipitation.
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        f"&timezone=auto"
    )
    st.info("Fetching 7‑day forecast data...")
    response = requests.get(url)
    if response.status_code != 200:
        st.error("Error fetching climate data. Please try again later.")
        return

    data = response.json()
    daily = data.get("daily", {})
    if not daily:
        st.error("No daily forecast data available from the API.")
        return

    # Create a DataFrame from the API response.
    df = pd.DataFrame({
        "Date": daily["time"],
        "Max Temperature (°C)": daily["temperature_2m_max"],
        "Min Temperature (°C)": daily["temperature_2m_min"],
        "Precipitation (mm)": daily["precipitation_sum"]
    })

    st.markdown("### 7‑Day Weather Forecast")
    st.dataframe(df)

    # Temperature Trends Line Chart.
    fig_temp = px.line(
        df, 
        x="Date", 
        y=["Max Temperature (°C)", "Min Temperature (°C)"],
        title="7‑Day Temperature Forecast",
        markers=True,
        template="plotly_white"
    )
    fig_temp.update_layout(xaxis_title="Date", yaxis_title="Temperature (°C)")
    st.plotly_chart(fig_temp, use_container_width=True)

    # Precipitation Bar Chart.
    fig_precip = px.bar(
        df, 
        x="Date", 
        y="Precipitation (mm)",
        title="7‑Day Precipitation Forecast",
        template="plotly_white"
    )
    fig_precip.update_layout(xaxis_title="Date", yaxis_title="Precipitation (mm)")
    st.plotly_chart(fig_precip, use_container_width=True)

    st.success("✅ Climate Insights loaded successfully!")

if __name__ == "__main__":
    climate_insights_dashboard()
