# climate_insights.py
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import config  # our config.py contains WEATHER_API_KEY and other settings

@st.cache_data(show_spinner=True, ttl=86400)
def fetch_weather_data(api_key, lat, lon, date_str):
    """
    Fetch historical weather data from WeatherAPI.com for a given location and date.
    Uses the History API endpoint. Date must be in YYYY-MM-DD format.
    """
    url = (
        f"http://api.weatherapi.com/v1/history.json?"
        f"key={api_key}&q={lat},{lon}&dt={date_str}&aqi=no&alerts=no"
    )
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def compute_yearly_climate(country, start_year=2012, end_year=2025, sample_date="09-15"):
    """
    For the selected country, fetch historical weather data on a representative day
    (by default September 15) for each year and compute key metrics.
    Returns a DataFrame with Year, Date, Max Temp, Total Rainfall, and a derived Crop Outcome.
    """
    # Define approximate coordinates for the key date-growing region in each country.
    location_mapping = {
        "Iraq": {"lat": 30.5085, "lon": 47.7836},  # Basra region
        "United Arab Emirates": {"lat": 24.207, "lon": 55.744},  # Al Ain approximate
        "Iran": {"lat": 31.3203, "lon": 48.6692},  # Khuzestan region
        "Saudi Arabia": {"lat": 24.7136, "lon": 46.6753},  # Riyadh region (example)
        "Tunisia": {"lat": 33.7047, "lon": 8.9692},  # Kebili region
        "Algeria": {"lat": 34.8555, "lon": 5.7280},  # Biskra region
        "Israel": {"lat": 31.5000, "lon": 35.3000},  # Jordan Valley approximate
        "Jordan": {"lat": 31.5000, "lon": 35.5000},  # Jordan Valley approximate
        "State of Palestine": {"lat": 31.8700, "lon": 35.4500}  # Jericho approximate
    }
    if country not in location_mapping:
        st.error(f"No location mapping available for {country}.")
        return pd.DataFrame()

    api_key = config.WEATHER_API_KEY
    lat = location_mapping[country]["lat"]
    lon = location_mapping[country]["lon"]

    results = []
    for year in range(start_year, end_year + 1):
        date_str = f"{year}-{sample_date}"  # e.g., "2012-09-15"
        try:
            data = fetch_weather_data(api_key, lat, lon, date_str)
            # Extract daily data from the response:
            day_data = data["forecast"]["forecastday"][0]["day"]
            max_temp = day_data.get("maxtemp_c")
            total_precip = day_data.get("totalprecip_mm")
            results.append({
                "Year": year,
                "Date": date_str,
                "Max Temp (°C)": max_temp,
                "Total Rainfall (mm)": total_precip
            })
        except Exception as e:
            st.error(f"Error fetching weather data for {year}: {e}")
            results.append({
                "Year": year,
                "Date": date_str,
                "Max Temp (°C)": None,
                "Total Rainfall (mm)": None
            })
    df = pd.DataFrame(results)

    # Define crop outcome based on thresholds.
    def determine_outcome(row):
        temp = row["Max Temp (°C)"]
        rain = row["Total Rainfall (mm)"]
        if temp is None or rain is None:
            return "Data Incomplete"
        # Example (adjust these thresholds as needed):
        if rain >= 14 and 37 <= temp <= 40:
            return "Excellent"
        elif rain >= 10 and 36 <= temp <= 41:
            return "Good"
        elif rain >= 5 and 35 <= temp <= 42:
            return "Moderate"
        else:
            return "Poor"
    df["Crop Outcome"] = df.apply(determine_outcome, axis=1)
    return df

def yearly_crop_review_dashboard(data: pd.DataFrame):
    st.title("🌦 Climate & Crop Outcome Insights for Dates")
    st.markdown("""
    This dashboard reviews historical weather data during the new crop season (harvest period) for dates.
    It uses WeatherAPI.com's history endpoint to fetch data for a representative day (by default September 15)
    for each year from 2012 to 2025. Based on the average maximum temperature and total rainfall,
    a crop outcome (e.g., Excellent, Good, Moderate, or Poor) is determined.
    """)
    # Let user select the country of interest.
    country = st.selectbox(
        "Select Country (Date-Growing Region):",
        ["Iraq", "United Arab Emirates", "Iran", "Saudi Arabia", "Tunisia", "Algeria", "Israel", "Jordan", "State of Palestine"]
    )

    with st.spinner("Fetching and analyzing historical climate data..."):
        climate_df = compute_yearly_climate(country)

    if climate_df.empty:
        st.error("No climate data available.")
        return

    st.subheader("Yearly Climate Summary")
    st.dataframe(climate_df)

    # Plot trends: dual-axis line chart for Max Temp and Rainfall.
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=climate_df["Year"],
        y=climate_df["Max Temp (°C)"],
        mode='lines+markers',
        name="Max Temp (°C)",
        line=dict(color='firebrick')
    ))
    fig.add_trace(go.Scatter(
        x=climate_df["Year"],
        y=climate_df["Total Rainfall (mm)"],
        mode='lines+markers',
        name="Total Rainfall (mm)",
        line=dict(color='royalblue'),
        yaxis="y2"
    ))
    fig.update_layout(
        title="Yearly Climate Trends",
        xaxis_title="Year",
        yaxis=dict(title="Max Temp (°C)"),
        yaxis2=dict(title="Total Rainfall (mm)", overlaying="y", side="right"),
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Combined Climate & Crop Outcome Insights")
    for _, row in climate_df.iterrows():
        st.markdown(f"**{int(row['Year'])}:** Avg Rainfall = {row['Total Rainfall (mm)']} mm, Avg Max Temp = {row['Max Temp (°C)']} °C → Dominant Outcome: **{row['Crop Outcome']}**")

    # Download option
    csv_data = climate_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Climate Insights as CSV", csv_data, "climate_insights.csv", "text/csv")
    st.success("✅ Climate Insights Dashboard loaded successfully!")
