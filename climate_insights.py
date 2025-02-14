# climate_insights.py
import streamlit as st
import pandas as pd
import plotly.express as px
import requests

def climate_insights_dashboard():
    st.title("🌦 Climate Insights for Date-Growing Regions")
    st.markdown("""
    This dashboard fetches a 7‑day weather forecast for the key date‑growing regions in select partner countries.  
    Select a partner country below to view its weather forecast.  
    *Data is fetched using the free Open‑Meteo API.*
    """)

    # Mapping of partner countries to approximate coordinates for key date-growing regions.
    # Based on:
    # Iraq – Basra; UAE – Al Ain; Iran – Khuzestan; Saudi Arabia – Eastern Province/Al-Ahsa; 
    # Tunisia – Gabes; Algeria – Biskra; Israel – Jordan Valley; Jordan – Near the Dead Sea; 
    # State of Palestine – Jericho region.
    partner_coords = {
        "IRAQ": {"lat": 30.5, "lon": 47.8},
        "UNITED ARAB EMIRATES": {"lat": 24.22, "lon": 55.75},
        "IRAN": {"lat": 31.3, "lon": 48.7},
        "SAUDI ARABIA": {"lat": 25.3, "lon": 49.5},
        "TUNISIA": {"lat": 33.9, "lon": 10.1},
        "ALGERIA": {"lat": 34.85, "lon": 5.73},
        "ISRAEL": {"lat": 31.5, "lon": 35.0},
        "JORDAN": {"lat": 31.6, "lon": 35.5},
        "STATE OF PALESTINE": {"lat": 31.9, "lon": 35.2}
    }

    partner_list = list(partner_coords.keys())
    selected_partner = st.selectbox("Select a Partner Country:", partner_list)

    coords = partner_coords.get(selected_partner)
    if not coords:
        st.error("Coordinates not found for the selected partner.")
        return

    st.markdown(f"**Fetching climate data for {selected_partner} (lat: {coords['lat']}, lon: {coords['lon']})**")

    # Build API URL for a 7‑day forecast (daily max/min temperature and precipitation) using Open‑Meteo.
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={coords['lat']}&longitude={coords['lon']}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
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
        "Date": daily.get("time", []),
        "Max Temperature (°C)": daily.get("temperature_2m_max", []),
        "Min Temperature (°C)": daily.get("temperature_2m_min", []),
        "Precipitation (mm)": daily.get("precipitation_sum", [])
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
