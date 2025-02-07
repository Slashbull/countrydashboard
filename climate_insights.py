# climate_insights.py
import streamlit as st
import pandas as pd
import altair as alt
import requests
from data_loader import load_data
from filters import add_filters

def fetch_climate_data(latitude, longitude, start_date, end_date):
    # Example API call using Open-Meteo (modify parameters as needed)
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_max,precipitation_sum",
        "timezone": "auto"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Error fetching climate data")
        return None

def show_climate_insights():
    st.header("Climate Insights")
    # Load and filter business data
    df = load_data()
    df = add_filters(df)
    st.write("Use the business data date range to correlate with climate data.")
    
    # For simplicity, use fixed coordinates (e.g., center of a region); in practice, this could be user-defined.
    latitude, longitude = 40.0, -100.0
    # Use the earliest and latest date in your dataset
    start_date = df["Date"].min().strftime("%Y-%m-%d")
    end_date = df["Date"].max().strftime("%Y-%m-%d")
    
    st.write(f"Fetching climate data from {start_date} to {end_date} for coordinates ({latitude}, {longitude})...")
    climate_data = fetch_climate_data(latitude, longitude, start_date, end_date)
    
    if climate_data:
        # Convert climate data into a DataFrame
        dates = climate_data["daily"]["time"]
        temps = climate_data["daily"]["temperature_2m_max"]
        precip = climate_data["daily"]["precipitation_sum"]
        df_climate = pd.DataFrame({
            "Date": pd.to_datetime(dates),
            "Max_Temperature": temps,
            "Precipitation": precip
        })
        st.write("Climate Data:")
        st.dataframe(df_climate)
        
        # Example: Plot Temperature trend
        temp_chart = alt.Chart(df_climate).mark_line(color="orange").encode(
            x='Date:T',
            y=alt.Y('Max_Temperature:Q', title="Max Temperature (°C)"),
            tooltip=['Date:T', 'Max_Temperature:Q']
        ).properties(width=700, height=300)
        st.altair_chart(temp_chart, use_container_width=True)
        
        # You can further correlate this climate data with your business data.
