import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# =============================================================================
# Define Crop Season Mapping for Date Cultivation (Harvest Period)
# =============================================================================
# For our purposes, we focus on the harvest season (New Crop) for each country.
CROP_SEASON = {
    "Iraq": {"start": "08-01", "end": "10-31"},
    "United Arab Emirates": {"start": "07-01", "end": "09-30"},
    "Iran": {"start": "08-01", "end": "10-31"},
    "Saudi Arabia": {"start": "07-01", "end": "10-31"},
    "Tunisia": {"start": "09-01", "end": "11-30"},
    "Algeria": {"start": "09-01", "end": "11-30"},
    "Israel": {"start": "08-01", "end": "10-31"},
    "Jordan": {"start": "08-01", "end": "10-31"},
    "State of Palestine": {"start": "08-01", "end": "10-31"}
}

# =============================================================================
# Define Region Coordinates for key sub‑regions (approximate)
# =============================================================================
REGION_COORDINATES = {
    "Iraq": {"Basra": (30.5085, 47.7835)},
    "United Arab Emirates": {"Al Ain": (24.2075, 55.7447)},
    "Iran": {"Khuzestan": (32.0, 48.0)},
    "Saudi Arabia": {"Al-Madinah": (24.467, 39.617)},
    "Tunisia": {"Kebili": (33.7037, 8.9708)},
    "Algeria": {"Biskra": (34.85, 5.73)},
    "Israel": {"Jordan Valley": (32.5, 35.5)},
    "Jordan": {"Jordan Valley": (31.5, 35.5)},
    "State of Palestine": {"Jericho": (31.87, 35.45)}
}

# =============================================================================
# Weather Data Fetching Function
# =============================================================================
def fetch_crop_season_weather(lat, lon, year, season_start, season_end):
    """
    Fetch daily historical weather data (max temperature and precipitation sum)
    for a given latitude, longitude and a crop season (start_date to end_date) in a given year.
    Uses the Open-Meteo Archive API.
    """
    start_date = f"{year}-{season_start}"
    end_date   = f"{year}-{season_end}"
    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={start_date}&end_date={end_date}"
        "&daily=temperature_2m_max,precipitation_sum"
        "&timezone=auto"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()
        json_data = response.json()
        daily = pd.DataFrame(json_data["daily"])
        daily["time"] = pd.to_datetime(daily["time"])
        return daily
    except Exception as e:
        st.error(f"Error fetching weather data for {year}: {e}")
        return pd.DataFrame()

# =============================================================================
# Crop Outcome Classification Logic
# =============================================================================
def classify_crop_outcome(avg_rainfall, avg_temp):
    """
    Classify the date crop outcome based on average monthly rainfall (mm) and 
    average maximum temperature (°C) during the harvest season.
    
    The thresholds below are illustrative – you may adjust them based on agronomic research.
    """
    if 14 <= avg_rainfall <= 17 and 37 <= avg_temp <= 40:
        return "Excellent"
    elif 10 <= avg_rainfall < 14 and 36 <= avg_temp <= 40:
        return "Good"
    elif 8 <= avg_rainfall < 10 or (35 <= avg_temp < 36 or 40 < avg_temp <= 42):
        return "Moderate"
    else:
        return "Poor"

# =============================================================================
# Main Dashboard Function for Yearly Crop Review Based on Harvest Season Climate
# =============================================================================
def yearly_crop_review_dashboard(_):
    st.title("🌦️ Yearly Crop Review for Date Cultivation")
    st.markdown("""
    This dashboard analyzes historical weather conditions during the harvest season for date‐cultivation.
    Select a country and sub‐region below, then review the yearly average climate (rainfall and maximum temperature)
    during the harvest period and the corresponding crop outcome classification.
    """)
    
    # Sidebar selections: Country, Sub-region, Year Range
    country = st.selectbox("Select Country:", list(CROP_SEASON.keys()))
    subregion = st.selectbox("Select Sub-region:", list(REGION_COORDINATES[country].keys()))
    lat, lon = REGION_COORDINATES[country][subregion]
    
    # Get crop season dates for the selected country.
    season = CROP_SEASON[country]
    st.info(f"For {country}, the harvest season is set from {season['start']} to {season['end']} (MM-DD format).")
    
    start_year = st.number_input("Start Year:", min_value=2012, max_value=2025, value=2012, step=1)
    end_year   = st.number_input("End Year:", min_value=start_year, max_value=2025, value=2023, step=1)
    years = list(range(int(start_year), int(end_year) + 1))
    
    st.info(f"Fetching harvest season weather data for {subregion}, {country} from {start_year} to {end_year}...")
    
    records = []
    for year in years:
        daily_df = fetch_crop_season_weather(lat, lon, year, season['start'], season['end'])
        if daily_df.empty:
            continue
        # Compute average maximum temperature over the season
        avg_temp = daily_df["temperature_2m_max"].mean()
        # Total precipitation over the season divided by number of months (approximate)
        total_precip = daily_df["precipitation_sum"].sum()
        # Determine the number of months in the season (based on season dates)
        start_month = int(season['start'].split("-")[0])
        end_month = int(season['end'].split("-")[0])
        n_months = end_month - start_month + 1
        avg_rainfall = total_precip / n_months if n_months > 0 else 0
        outcome = classify_crop_outcome(avg_rainfall, avg_temp)
        records.append({
            "Year": year,
            "Avg Rainfall (mm)": round(avg_rainfall, 2),
            "Avg Max Temp (°C)": round(avg_temp, 2),
            "Dominant Outcome": outcome
        })
    
    if not records:
        st.error("No weather data available for the selected period and region.")
        return
    
    result_df = pd.DataFrame(records)
    st.markdown("### Automated Yearly Insights")
    st.dataframe(result_df)
    
    # Visualization: Line Charts for Rainfall and Temperature
    fig_rain = px.line(result_df, x="Year", y="Avg Rainfall (mm)", markers=True, 
                         title="Average Monthly Rainfall During Harvest Season", 
                         template="plotly_white")
    fig_temp = px.line(result_df, x="Year", y="Avg Max Temp (°C)", markers=True, 
                         title="Average Maximum Temperature During Harvest Season", 
                         template="plotly_white")
    
    # Annotate outcomes on a bar chart
    fig_outcome = px.bar(result_df, x="Year", y="Avg Rainfall (mm)", 
                         title="Yearly Average Rainfall & Crop Outcome", 
                         text="Dominant Outcome", 
                         template="plotly_white")
    
    st.plotly_chart(fig_rain, use_container_width=True)
    st.plotly_chart(fig_temp, use_container_width=True)
    st.plotly_chart(fig_outcome, use_container_width=True)
    
    # Download the aggregated data as CSV
    csv_data = result_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Yearly Crop Review Data as CSV", csv_data, "yearly_crop_review.csv", "text/csv")
    
    st.success("✅ Yearly Crop Review loaded successfully!")

# For standalone testing
if __name__ == "__main__":
    yearly_crop_review_dashboard(None)
