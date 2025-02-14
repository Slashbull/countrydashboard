# climate_insights.py
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime, timedelta

# Example heuristic thresholds (modify based on domain research)
RAINFALL_THRESHOLDS = {
    "Excellent": (14, 17),  # mm (monthly average)
    "Good": (11, 14),
    "Moderate": (8, 11),
    "Poor": (0, 8)
}
TEMP_THRESHOLDS = {
    "Excellent": (37, 39),  # °C (monthly average max temperature)
    "Good": (39, 40),
    "Moderate": (40, 42),
    "Poor": (42, 50)
}

def classify_crop_outcome(avg_rainfall, avg_temp):
    """
    Classify crop outcome based on heuristic thresholds for rainfall and temperature.
    """
    def get_class(value, thresholds):
        for outcome, (low, high) in thresholds.items():
            if low <= value < high:
                return outcome
        return "Unknown"

    rainfall_class = get_class(avg_rainfall, RAINFALL_THRESHOLDS)
    temp_class = get_class(avg_temp, TEMP_THRESHOLDS)
    
    # Combine rules (this is a simple rule: if both are Excellent, outcome is Excellent; otherwise, take the worst)
    outcomes = {"Excellent": 4, "Good": 3, "Moderate": 2, "Poor": 1, "Unknown": 0}
    overall = min(outcomes.get(rainfall_class, 0), outcomes.get(temp_class, 0))
    for key, val in outcomes.items():
        if val == overall:
            return key
    return "Unknown"

def fetch_weather_data(latitude, longitude, start_date, end_date):
    """
    Fetch monthly weather data from Open-Meteo's ERA5 API.
    Adjust parameters based on the Open-Meteo documentation.
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
        # Convert to DataFrame
        daily = pd.DataFrame(data["daily"])
        daily["time"] = pd.to_datetime(daily["time"])
        daily.set_index("time", inplace=True)
        monthly = daily.resample("M").mean().reset_index()
        monthly["Year"] = monthly["time"].dt.year
        monthly["Month"] = monthly["time"].dt.strftime("%b")
        return monthly
    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return pd.DataFrame()

def yearly_crop_review_dashboard(data: pd.DataFrame):
    st.title("🌦 Climate & Crop Outcome Analysis for Date Cultivation")
    st.markdown("""
    This dashboard provides a yearly review of climate conditions and estimates the dominant crop outcome for date cultivation.
    *Optimal conditions are based on heuristic thresholds for rainfall and temperature.*
    """)

    # For this example, we'll focus on Saudi Arabia's key date-growing regions.
    # Use approximate coordinates for a central region (e.g., Riyadh)
    latitude, longitude = 24.7136, 46.6753  # Coordinates for Riyadh (adjust as needed)
    
    # Define time range from 2012 to current year (or a specified end date)
    start_date = "2012-01-01"
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    weather_df = fetch_weather_data(latitude, longitude, start_date, end_date)
    if weather_df.empty:
        st.error("No weather data available.")
        return

    # Calculate dominant outcome per year based on average rainfall and temperature.
    # (In a real scenario, you would use more detailed metrics and possibly additional climate factors.)
    results = []
    for year in sorted(weather_df["Year"].unique()):
        yearly_data = weather_df[weather_df["Year"] == year]
        avg_rainfall = yearly_data["precipitation_sum"].mean()  # mm
        avg_temp = yearly_data["temperature_2m_max"].mean()  # °C
        outcome = classify_crop_outcome(avg_rainfall, avg_temp)
        results.append({
            "Year": year,
            "Avg Rainfall (mm)": round(avg_rainfall, 1),
            "Avg Max Temp (°C)": round(avg_temp, 1),
            "Dominant Outcome": outcome
        })
    results_df = pd.DataFrame(results)

    st.subheader("Yearly Climate & Crop Outcome Review")
    st.dataframe(results_df)

    fig = px.bar(results_df, x="Year", y="Avg Rainfall (mm)", color="Dominant Outcome",
                 title="Yearly Average Rainfall with Crop Outcome",
                 text="Avg Rainfall (mm)", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.bar(results_df, x="Year", y="Avg Max Temp (°C)", color="Dominant Outcome",
                  title="Yearly Average Max Temperature with Crop Outcome",
                  text="Avg Max Temp (°C)", template="plotly_white")
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Download Review Data")
    csv_data = results_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Review as CSV", csv_data, "yearly_crop_review.csv", "text/csv")

if __name__ == "__main__":
    yearly_crop_review_dashboard(pd.DataFrame())
