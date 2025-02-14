import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta

# ------------------------------
# Helper functions
# ------------------------------

def get_weather_data(latitude: float, longitude: float, start_date: str, end_date: str):
    """
    Fetch historical weather data (daily rainfall and temperature) from Open-Meteo API.
    For demonstration, we assume that the API endpoint returns:
       - daily: time, temperature_2m_max, temperature_2m_min, precipitation_sum
    """
    base_url = "https://api.open-meteo.com/v1/era5"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto"
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()
    if "daily" not in data:
        st.error("No daily weather data returned.")
        return pd.DataFrame()
    
    df = pd.DataFrame(data["daily"])
    # Compute average temperature for each day
    df["temperature_avg"] = (df["temperature_2m_max"] + df["temperature_2m_min"]) / 2
    df["date"] = pd.to_datetime(df["time"])
    return df

def evaluate_crop_outcome(avg_rainfall, avg_temp):
    """
    Simple rule-based evaluation of date crop outcome based on average rainfall and temperature.
    These thresholds are for demonstration only.
    """
    # Example thresholds (you should adjust based on agronomic knowledge):
    # For dates, optimal conditions might be moderate to high temperatures and moderate rainfall.
    if avg_rainfall >= 16 and 36 <= avg_temp <= 38:
        return "Excellent"
    elif 14 <= avg_rainfall < 16 and 36 <= avg_temp <= 39:
        return "Good"
    elif 12 <= avg_rainfall < 14 and 37 <= avg_temp <= 40:
        return "Moderate"
    else:
        return "Poor"

def generate_yearly_summary(weather_df: pd.DataFrame):
    """
    Compute yearly averages for rainfall and temperature and determine crop outcome.
    """
    weather_df["year"] = weather_df["date"].dt.year
    summary = weather_df.groupby("year").agg({
        "precipitation_sum": "mean",
        "temperature_avg": "mean"
    }).reset_index()
    summary.rename(columns={"precipitation_sum": "avg_rainfall", "temperature_avg": "avg_temp"}, inplace=True)
    summary["Crop Outcome"] = summary.apply(
        lambda row: evaluate_crop_outcome(row["avg_rainfall"], row["avg_temp"]), axis=1
    )
    return summary

# ------------------------------
# Main Dashboard Function
# ------------------------------

def yearly_crop_review_dashboard(data: pd.DataFrame):
    st.title("🌦 Yearly Crop Review Based on Climate Data")
    st.markdown("""
    This module fetches historical climate data (rainfall and temperature) for a given partner region 
    and provides a yearly review of how the conditions may have affected date crop outcomes.
    """)

    # For demonstration, we’ll assume the partner of interest is Saudi Arabia – focusing on the Al-Madinah region.
    st.subheader("Select Region (Partner)")
    # In a real application, you might allow selection among multiple regions.
    region = st.selectbox("Region", ["Al-Madinah"], index=0)
    
    # Define coordinates for the region (Al-Madinah in Saudi Arabia)
    # (These coordinates are approximate; you should verify and adjust them as needed.)
    region_coords = {
        "Al-Madinah": {"latitude": 24.5247, "longitude": 39.5692}
    }
    
    coords = region_coords.get(region)
    if not coords:
        st.error("No coordinate mapping available for the selected region.")
        return

    # Define the date range for historical data. For example, from 2012-01-01 to today.
    start_date = "2012-01-01"
    end_date = datetime.today().strftime("%Y-%m-%d")
    st.info(f"Fetching weather data for {region} from {start_date} to {end_date}...")

    try:
        weather_df = get_weather_data(coords["latitude"], coords["longitude"], start_date, end_date)
    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return

    if weather_df.empty:
        st.error("No weather data available.")
        return

    # Generate yearly summary insights.
    yearly_summary = generate_yearly_summary(weather_df)

    st.markdown("## Automated Yearly Insights")
    st.dataframe(yearly_summary.style.format({
        "avg_rainfall": "{:.1f} mm",
        "avg_temp": "{:.1f}°C"
    }))

    # Create a line chart for rainfall and temperature over time.
    st.markdown("## Climate Trends Over Time")
    fig = px.line(weather_df, x="date", y=["precipitation_sum", "temperature_avg"],
                  labels={"value": "Measurement", "date": "Date"},
                  title="Daily Rainfall and Average Temperature")
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    # Display overall insights in markdown.
    st.markdown("### Summary of Date Crop Conditions")
    for index, row in yearly_summary.iterrows():
        st.markdown(f"**{row['year']}**: Avg Rainfall = {row['avg_rainfall']:.1f} mm, "
                    f"Avg Temp = {row['avg_temp']:.1f}°C, Dominant Outcome: **{row['Crop Outcome']}**")
    
    st.success("✅ Yearly Crop Review Dashboard loaded successfully!")

# For testing purposes, if running this module standalone:
if __name__ == "__main__":
    # For standalone testing, simulate some input data
    # (In production, the 'data' parameter would be your main trade DataFrame.)
    dummy_data = pd.DataFrame({
        "Reporter": ["India"] * 10,
        "Flow": ["Import"] * 10,
        "Partner": ["Saudi Arabia"] * 10,
        "Code": [804] * 10,
        "Desc": ["Dates and related fruits"] * 10,
        "Tons": np.random.uniform(100, 1000, size=10),
        "Year": np.random.choice([2012, 2013, 2014, 2015], size=10),
        "Month": np.random.choice(["Jan", "Feb", "Mar", "Apr"], size=10)
    })
    # Create a dummy 'Period' column (for compatibility with other modules)
    dummy_data["Period_dt"] = pd.to_datetime(dummy_data["Month"] + "-" + dummy_data["Year"].astype(str), format="%b-%Y")
    dummy_data["Period"] = dummy_data["Period_dt"].dt.strftime("%b-%Y")
    
    yearly_crop_review_dashboard(dummy_data)
