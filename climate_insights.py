# climate_insights.py
import streamlit as st
import pandas as pd
import altair as alt
import requests
from io import StringIO
from filters import add_filters
import config

def fetch_climate_data(latitude, longitude, start_date, end_date):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_max,precipitation_sum",
        "timezone": "auto"
    }
    response = requests.get(config.OPEN_METEO_API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error fetching climate data")
        return None

def show_climate_insights():
    st.header("Climate Insights")
    from core_system import data  # Global data
    df_filtered = add_filters(data)
    if df_filtered.empty:
        st.warning("No business data available for climate correlation.")
        return
    start_date = df_filtered["Date"].min().strftime("%Y-%m-%d")
    end_date = df_filtered["Date"].max().strftime("%Y-%m-%d")
    st.write(f"Fetching climate data from {start_date} to {end_date}...")
    latitude, longitude = 40.0, -100.0  # For demonstration; adjust as needed
    climate_json = fetch_climate_data(latitude, longitude, start_date, end_date)
    if climate_json:
        dates = climate_json["daily"]["time"]
        temps = climate_json["daily"]["temperature_2m_max"]
        precip = climate_json["daily"]["precipitation_sum"]
        df_climate = pd.DataFrame({
            "Date": pd.to_datetime(dates),
            "Max_Temperature": temps,
            "Precipitation": precip
        })
        st.write("Climate Data:")
        st.dataframe(df_climate)
        temp_chart = alt.Chart(df_climate).mark_line(color="orange").encode(
            x='Date:T',
            y=alt.Y('Max_Temperature:Q', title="Max Temperature (°C)"),
            tooltip=['Date:T', 'Max_Temperature:Q']
        ).properties(width=700, height=300)
        st.altair_chart(temp_chart, use_container_width=True)
    else:
        st.error("No climate data available.")
