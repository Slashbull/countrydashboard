import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

# ------------------------------
# Helper Functions
# ------------------------------

def get_weather_data(latitude: float, longitude: float, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Fetch historical weather data from the Open‑Meteo ERA5 Archive API.
    Uses the latest endpoint as per the documentation:
      https://open-meteo.com/en/docs/historical-weather-api
    
    Parameters:
      - latitude: Latitude of the location.
      - longitude: Longitude of the location.
      - start_date: Start date (YYYY-MM-DD).
      - end_date: End date (YYYY-MM-DD).
    
    Returns:
      - A DataFrame containing daily max/min temperatures and precipitation sum,
        plus a computed average temperature and converted date column.
    """
    base_url = "https://archive-api.open-meteo.com/v1/era5"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "auto"
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an error for HTTP issues
        data = response.json()
    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return pd.DataFrame()

    if "daily" not in data:
        st.error("No daily weather data returned by the API.")
        return pd.DataFrame()
    
    df = pd.DataFrame(data["daily"])
    # Compute the daily average temperature
    df["temperature_avg"] = (df["temperature_2m_max"] + df["temperature_2m_min"]) / 2
    # Convert the time column to datetime
    df["date"] = pd.to_datetime(df["time"])
    return df

def evaluate_crop_outcome(avg_rainfall: float, avg_temp: float) -> str:
    """
    Evaluate date crop outcome based on average rainfall and temperature.
    
    These thresholds are examples; adjust them based on expert insights for date cultivation.
    For example, in your use case, conditions may be:
      - Excellent: avg_rainfall >= 14 mm and avg_temp between 37°C and 39°C
      - Good:      avg_rainfall between 12 and 14 mm and avg_temp between 37°C and 40°C
      - Moderate:  avg_rainfall between 10 and 12 mm or avg_temp slightly outside optimal range
      - Poor:      Otherwise.
    """
    if avg_rainfall >= 14 and 37 <= avg_temp <= 39:
        return "Excellent"
    elif 12 <= avg_rainfall < 14 and 37 <= avg_temp <= 40:
        return "Good"
    elif 10 <= avg_rainfall < 12 or not (36 <= avg_temp <= 40):
        return "Moderate"
    else:
        return "Poor"

def generate_yearly_summary(weather_df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a yearly summary DataFrame from daily weather data.
    Computes the average daily precipitation and temperature per year,
    then determines the dominant crop outcome based on these averages.
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
    st.title("🌦 Yearly Date Crop Review Based on Climate Data")
    st.markdown("""
    This module retrieves historical climate data for a specified region and calculates yearly averages 
    for rainfall and temperature. Based on these metrics, it evaluates the expected outcome of date crops.
    """)
    
    # For this example, we focus on a region in Saudi Arabia where dates are predominantly grown.
    st.subheader("Select Region")
    # Extend this dictionary if you wish to include more regions.
    region = st.selectbox("Region", ["Al-Madinah"], index=0)
    region_coords = {
        "Al-Madinah": {"latitude": 24.5247, "longitude": 39.5692}  # Approximate coordinates
    }
    coords = region_coords.get(region)
    if not coords:
        st.error("No coordinate mapping available for the selected region.")
        return

    # Define the date range for historical data.
    start_date = "2012-01-01"
    end_date = datetime.today().strftime("%Y-%m-%d")
    st.info(f"Fetching weather data for {region} from {start_date} to {end_date}...")

    weather_df = get_weather_data(coords["latitude"], coords["longitude"], start_date, end_date)
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

    # Create an interactive line chart for daily climate trends.
    st.markdown("## Daily Climate Trends")
    fig = px.line(weather_df, x="date", y=["precipitation_sum", "temperature_avg"],
                  labels={"value": "Measurement", "date": "Date"},
                  title="Daily Rainfall and Average Temperature Trends")
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Yearly Crop Outcome Summary")
    for _, row in yearly_summary.iterrows():
        st.markdown(f"**{row['year']}**: Avg Rainfall = {row['avg_rainfall']:.1f} mm, "
                    f"Avg Temp = {row['avg_temp']:.1f}°C, Dominant Outcome: **{row['Crop Outcome']}**")
    
    st.success("✅ Yearly Date Crop Review Dashboard loaded successfully!")

# For standalone testing
if __name__ == "__main__":
    # For testing, you can simulate with a dummy DataFrame. In production, 'data' is your trade data.
    dummy_data = pd.DataFrame({
        "Reporter": ["India"] * 10,
        "Flow": ["Import"] * 10,
        "Partner": ["Saudi Arabia"] * 10,
        "Code": [804] * 10,
        "Desc": ["Dates and related fruits"] * 10,
        "Tons": [1000, 2000, 1500, 2500, 1800, 2200, 1700, 2100, 1900, 2300],
        "Year": [2012, 2012, 2013, 2013, 2014, 2014, 2015, 2015, 2016, 2016],
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct"]
    })
    # Create a dummy 'Period' column
    dummy_data["Period_dt"] = pd.to_datetime(dummy_data["Month"] + "-" + dummy_data["Year"].astype(str), format="%b-%Y")
    dummy_data["Period"] = dummy_data["Period_dt"].dt.strftime("%b-%Y")
    yearly_crop_review_dashboard(dummy_data)
