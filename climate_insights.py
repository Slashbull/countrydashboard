# climate_insights.py
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

# --- Heuristic classification for date crop outcome ---
def classify_crop_outcome(avg_rainfall, avg_temp):
    """
    Classify the crop outcome based on average monthly total rainfall (mm) and 
    average max temperature (°C). (Heuristic thresholds for date palms are used here.)
    """
    # For precipitation, assume that monthly totals between about 12 and 17 mm are optimal.
    if 12 <= avg_rainfall <= 17:
        rainfall_score = 1.0
    elif 10 <= avg_rainfall < 12 or 17 < avg_rainfall <= 20:
        rainfall_score = 0.8
    elif 8 <= avg_rainfall < 10 or 20 < avg_rainfall <= 22:
        rainfall_score = 0.6
    else:
        rainfall_score = 0.4

    # For temperature, assume that maximum temperatures between 37 and 40°C are best.
    if 37 <= avg_temp <= 40:
        temp_score = 1.0
    elif 35 <= avg_temp < 37 or 40 < avg_temp <= 42:
        temp_score = 0.8
    elif 33 <= avg_temp < 35 or 42 < avg_temp <= 44:
        temp_score = 0.6
    else:
        temp_score = 0.4

    score = (rainfall_score + temp_score) / 2

    if score >= 0.9:
        return "Excellent"
    elif score >= 0.75:
        return "Good"
    elif score >= 0.6:
        return "Moderate"
    else:
        return "Poor"

# --- Fetch weather data from Open-Meteo Archive API ---
def fetch_weather_data(latitude, longitude, start_date, end_date):
    """
    Fetches daily weather data (precipitation_sum and temperature_2m_max) from 
    Open-Meteo’s Archive API, then aggregates it to monthly data.
    For precipitation, the daily totals are summed over the month;
    For temperature, the daily maximum temperatures are averaged.
    """
    base_url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "precipitation_sum,temperature_2m_max",
        "timezone": "auto"
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        daily = pd.DataFrame(data["daily"])
        daily["time"] = pd.to_datetime(daily["time"])
        daily.set_index("time", inplace=True)
        # For precipitation, use the sum; for temperature, the mean
        monthly = daily.resample("M").agg({
            "precipitation_sum": "sum",
            "temperature_2m_max": "mean"
        }).reset_index()
        monthly["Year"] = monthly["time"].dt.year
        monthly["Month"] = monthly["time"].dt.strftime("%b")
        return monthly
    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return pd.DataFrame()

# --- Main Dashboard Function ---
def yearly_crop_review_dashboard(dummy_df=None):
    st.title("🌦 Climate & Date Crop Outcome Analysis")
    st.markdown("""
    This module reviews historical climate conditions for a key date‐growing region 
    (e.g., Saudi Arabia – Al‑Qassim, Al‑Madinah, Riyadh, Eastern Province) and estimates 
    the dominant date crop outcome each year based on monthly total rainfall and average max temperature.
    """)
    
    # Coordinates for a representative region (e.g., Riyadh)
    latitude, longitude = 24.7136, 46.6753  
    start_date = "2012-01-01"
    end_date = datetime.now().strftime("%Y-%m-%d")

    weather_df = fetch_weather_data(latitude, longitude, start_date, end_date)
    if weather_df.empty:
        st.error("No weather data available. Please check API access and parameters.")
        return

    # Compute yearly averages:
    # - For rainfall: compute the average monthly total (in mm)
    # - For temperature: compute the average monthly maximum temperature (in °C)
    yearly = weather_df.groupby("Year").agg({
        "precipitation_sum": "mean",
        "temperature_2m_max": "mean"
    }).reset_index()
    yearly.rename(columns={
        "precipitation_sum": "Avg Rainfall (mm)",
        "temperature_2m_max": "Avg Max Temp (°C)"
    }, inplace=True)

    # Classify the dominant crop outcome for each year.
    yearly["Dominant Outcome"] = yearly.apply(
        lambda row: classify_crop_outcome(row["Avg Rainfall (mm)"], row["Avg Max Temp (°C)"]),
        axis=1
    )

    # Display the results.
    st.subheader("Automated Yearly Review")
    st.dataframe(yearly)

    # Visualizations: Bar charts for rainfall and temperature.
    fig_rain = px.bar(
        yearly,
        x="Year",
        y="Avg Rainfall (mm)",
        color="Dominant Outcome",
        title="Yearly Average Rainfall (mm) & Crop Outcome",
        text="Avg Rainfall (mm)",
        template="plotly_white"
    )
    st.plotly_chart(fig_rain, use_container_width=True)

    fig_temp = px.bar(
        yearly,
        x="Year",
        y="Avg Max Temp (°C)",
        color="Dominant Outcome",
        title="Yearly Average Max Temperature (°C) & Crop Outcome",
        text="Avg Max Temp (°C)",
        template="plotly_white"
    )
    st.plotly_chart(fig_temp, use_container_width=True)

    st.markdown("### Combined Climate & Outcome Insights")
    for _, row in yearly.iterrows():
        st.markdown(f"**{row['Year']}**: Avg Rainfall = **{row['Avg Rainfall (mm)']:.1f} mm**, "
                    f"Avg Max Temp = **{row['Avg Max Temp (°C)']:.1f} °C** → **{row['Dominant Outcome']}**")

    # Download button for the yearly review data.
    csv_data = yearly.to_csv(index=False).encode("utf-8")
    st.download_button("Download Yearly Review as CSV", csv_data, "yearly_crop_review.csv", "text/csv")

if __name__ == "__main__":
    # For testing purposes; in the full app, this function is called from core_system.py.
    yearly_crop_review_dashboard()
