# climate_insights.py
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

# --- Heuristic thresholds for Date Palm Crop Outcome ---
def classify_crop_outcome(avg_rainfall, avg_temp):
    """
    Classify the expected crop outcome for date cultivation based on
    average rainfall (mm) and average max temperature (°C).
    
    These thresholds are heuristic and based on typical conditions for dates:
      - Optimal rainfall: 12-17 mm per month.
      - Optimal max temperature: 37-39°C.
    """
    # Rainfall score
    if 12 <= avg_rainfall <= 17:
        rainfall_score = 1.0
    elif 10 <= avg_rainfall < 12 or 17 < avg_rainfall <= 19:
        rainfall_score = 0.8
    elif 8 <= avg_rainfall < 10 or 19 < avg_rainfall <= 21:
        rainfall_score = 0.6
    else:
        rainfall_score = 0.4

    # Temperature score
    if 37 <= avg_temp <= 39:
        temp_score = 1.0
    elif 35 <= avg_temp < 37 or 39 < avg_temp <= 41:
        temp_score = 0.8
    elif 33 <= avg_temp < 35 or 41 < avg_temp <= 43:
        temp_score = 0.6
    else:
        temp_score = 0.4

    # Combined score (average of both)
    score = (rainfall_score + temp_score) / 2
    if score >= 0.9:
        return "Excellent"
    elif score >= 0.75:
        return "Good"
    elif score >= 0.6:
        return "Moderate"
    else:
        return "Poor"

# --- Fetch Weather Data from Open-Meteo Archive API ---
def fetch_weather_data(latitude, longitude, start_date, end_date):
    """
    Fetch historical daily weather data (max temperature and precipitation sum)
    from Open-Meteo’s Archive API and return a DataFrame resampled to monthly averages.
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
        # Resample to monthly averages
        monthly = daily.resample("M").mean().reset_index()
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
    This dashboard reviews historical climate conditions for a key date‐growing region 
    (e.g., Saudi Arabia – Al‑Qassim, Al‑Madinah, Riyadh, Eastern Province) and estimates 
    the dominant date crop outcome each year based on average rainfall and maximum temperature.
    """)
    
    # Coordinates for a representative region (e.g., Riyadh)
    latitude, longitude = 24.7136, 46.6753  
    start_date = "2012-01-01"
    end_date = datetime.now().strftime("%Y-%m-%d")

    weather_df = fetch_weather_data(latitude, longitude, start_date, end_date)
    if weather_df.empty:
        st.error("No weather data available. Please check your API access and parameters.")
        return

    # Calculate yearly averages from the monthly data
    yearly = weather_df.groupby("Year").agg({
        "precipitation_sum": "mean",
        "temperature_2m_max": "mean"
    }).reset_index()
    yearly.rename(columns={
        "precipitation_sum": "Avg Rainfall (mm)",
        "temperature_2m_max": "Avg Max Temp (°C)"
    }, inplace=True)

    # Classify crop outcome for each year
    yearly["Dominant Outcome"] = yearly.apply(
        lambda row: classify_crop_outcome(row["Avg Rainfall (mm)"], row["Avg Max Temp (°C)"]),
        axis=1
    )

    # Display the results in a table
    st.subheader("Automated Yearly Review")
    st.dataframe(yearly)

    # Create visualizations
    fig_rain = px.bar(
        yearly, x="Year", y="Avg Rainfall (mm)",
        color="Dominant Outcome",
        title="Yearly Average Rainfall (mm) & Crop Outcome",
        text="Avg Rainfall (mm)",
        template="plotly_white"
    )
    st.plotly_chart(fig_rain, use_container_width=True)

    fig_temp = px.bar(
        yearly, x="Year", y="Avg Max Temp (°C)",
        color="Dominant Outcome",
        title="Yearly Average Max Temperature (°C) & Crop Outcome",
        text="Avg Max Temp (°C)",
        template="plotly_white"
    )
    st.plotly_chart(fig_temp, use_container_width=True)

    # Optionally, show combined insights
    st.markdown("### Combined Climate & Outcome Insights")
    for _, row in yearly.iterrows():
        st.markdown(f"**{row['Year']}**: Avg Rainfall = **{row['Avg Rainfall (mm)']:.1f} mm**, "
                    f"Avg Max Temp = **{row['Avg Max Temp (°C)']:.1f} °C** → **{row['Dominant Outcome']}**")

    # Download option
    csv_data = yearly.to_csv(index=False).encode("utf-8")
    st.download_button("Download Yearly Review as CSV", csv_data, "yearly_crop_review.csv", "text/csv")

if __name__ == "__main__":
    # For testing purposes only. In the actual app, this function is called from core_system.py.
    yearly_crop_review_dashboard()
