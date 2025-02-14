# date_crop_analysis.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from prophet import Prophet
import requests
from datetime import datetime

# ---------------------------
# Helper: Assess Date Crop Quality
# ---------------------------
def assess_date_crop_quality(df):
    """
    Assess date crop quality based on average daily precipitation and average maximum temperature.
    For date palms, lower precipitation (mm/day) and high but not excessive max temperatures are ideal.
    
    Precipitation thresholds (mm/day):
      - < 0.5  -> Excellent (score 5)
      - 0.5-0.7 -> Very Good (4)
      - 0.7-0.9 -> Good (3)
      - 0.9-1.1 -> Moderate (2)
      - >= 1.1  -> Bad (1)
    
    Maximum Temperature thresholds (°C) – Ideal is roughly 38-42°C:
      - Between 38 and 42 -> Excellent (5)
      - 36-38 or 42-44   -> Very Good (4)
      - 34-36 or 44-46   -> Good (3)
      - 32-34 or 46-48   -> Moderate (2)
      - Otherwise       -> Bad (1)
    
    Overall score = 0.6 * (Precipitation Score) + 0.4 * (Temperature Score)
    Then:
      - >= 4.5 : EXCELLENT
      - >= 4   : VERY GOOD
      - >= 3   : GOOD
      - >= 2   : MODERATE
      - Else   : BAD
    """
    avg_precip = df["Precipitation (mm)"].mean()
    avg_max_temp = df["Max Temperature (°C)"].mean()
    
    # Precipitation score
    if avg_precip < 0.5:
        p_score = 5
    elif avg_precip < 0.7:
        p_score = 4
    elif avg_precip < 0.9:
        p_score = 3
    elif avg_precip < 1.1:
        p_score = 2
    else:
        p_score = 1

    # Maximum temperature score
    if 38 <= avg_max_temp <= 42:
        t_score = 5
    elif (36 <= avg_max_temp < 38) or (42 < avg_max_temp <= 44):
        t_score = 4
    elif (34 <= avg_max_temp < 36) or (44 < avg_max_temp <= 46):
        t_score = 3
    elif (32 <= avg_max_temp < 34) or (46 < avg_max_temp <= 48):
        t_score = 2
    else:
        t_score = 1

    overall_score = 0.6 * p_score + 0.4 * t_score
    if overall_score >= 4.5:
        rating = "EXCELLENT"
    elif overall_score >= 4:
        rating = "VERY GOOD"
    elif overall_score >= 3:
        rating = "GOOD"
    elif overall_score >= 2:
        rating = "MODERATE"
    else:
        rating = "BAD"
        
    return rating, overall_score, avg_precip, avg_max_temp

# ---------------------------
# Helper: Fetch 7-Day Climate Forecast Data
# ---------------------------
def fetch_climate_data(coords):
    """
    Fetch a 7-day weather forecast from the Open-Meteo API for given coordinates.
    Returns a DataFrame with Date, Max/Min Temperature and Precipitation.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={coords['lat']}&longitude={coords['lon']}&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        f"&timezone=auto"
    )
    response = requests.get(url)
    if response.status_code != 200:
        st.error("Error fetching climate data. Please try again later.")
        return None
    data = response.json()
    daily = data.get("daily", {})
    if not daily:
        st.error("No daily forecast data available from the API.")
        return None
    df = pd.DataFrame({
        "Date": daily.get("time", []),
        "Max Temperature (°C)": daily.get("temperature_2m_max", []),
        "Min Temperature (°C)": daily.get("temperature_2m_min", []),
        "Precipitation (mm)": daily.get("precipitation_sum", [])
    })
    try:
        df["Date"] = pd.to_datetime(df["Date"])
    except Exception as e:
        st.error("Error converting Date to datetime.")
        st.error(e)
        return None
    return df

# ---------------------------
# Main Dashboard Function
# ---------------------------
def date_crop_analysis_dashboard():
    st.title("🌴 Date Crop Quality Analysis Dashboard")
    st.markdown("""
    This dashboard estimates the expected quality of date crops based on forecast climate conditions.
    
    **Key Considerations:**
    - **Precipitation:** Date palms thrive in arid environments. Too much rainfall can harm the crop.
    - **Temperature:** High temperatures are needed, but they must remain within an optimal range.
    
    The system combines these factors to produce a quality rating:
    **EXCELLENT, VERY GOOD, GOOD, MODERATE, BAD**
    """)

    # Mapping of partner countries to coordinates of key date-growing regions.
    partner_coords = {
        "IRAQ": {"lat": 30.5, "lon": 47.8},                # Basra region
        "UNITED ARAB EMIRATES": {"lat": 24.22, "lon": 55.75},# Al Ain region
        "IRAN": {"lat": 31.3, "lon": 48.7},                  # Khuzestan region
        "SAUDI ARABIA": {"lat": 25.3, "lon": 49.5},          # Eastern Province/Al-Ahsa
        "TUNISIA": {"lat": 33.9, "lon": 10.1},               # Gabes region
        "ALGERIA": {"lat": 34.85, "lon": 5.73},              # Biskra region
        "ISRAEL": {"lat": 31.5, "lon": 35.0},                # Jordan Valley/Negev
        "JORDAN": {"lat": 31.6, "lon": 35.5},                # Near the Dead Sea
        "STATE OF PALESTINE": {"lat": 31.9, "lon": 35.2}     # Jericho region
    }
    partner_list = list(partner_coords.keys())
    selected_country = st.selectbox("Select a Date-Growing Country:", partner_list)
    coords = partner_coords.get(selected_country)
    if not coords:
        st.error("Coordinates not found for the selected country.")
        return

    st.markdown(f"**Fetching 7‑day climate forecast for {selected_country} (lat: {coords['lat']}, lon: {coords['lon']})**")
    climate_df = fetch_climate_data(coords)
    if climate_df is None:
        return

    st.markdown("### 7‑Day Weather Forecast")
    st.dataframe(climate_df)

    # Display temperature and precipitation charts.
    fig_temp = px.line(
        climate_df,
        x="Date",
        y=["Max Temperature (°C)", "Min Temperature (°C)"],
        title="7‑Day Temperature Forecast",
        markers=True,
        template="plotly_white"
    )
    fig_temp.update_layout(xaxis_title="Date", yaxis_title="Temperature (°C)")
    st.plotly_chart(fig_temp, use_container_width=True)

    fig_precip = px.bar(
        climate_df,
        x="Date",
        y="Precipitation (mm)",
        title="7‑Day Precipitation Forecast",
        template="plotly_white"
    )
    fig_precip.update_layout(xaxis_title="Date", yaxis_title="Precipitation (mm)")
    st.plotly_chart(fig_precip, use_container_width=True)

    st.markdown("---")
    st.header("Crop Quality Assessment")
    st.markdown("Assessing the expected date crop quality based on forecasted climate conditions over the next 7 days.")

    # Calculate average conditions.
    avg_precip = climate_df["Precipitation (mm)"].mean()
    avg_max_temp = climate_df["Max Temperature (°C)"].mean()
    st.markdown(f"**Average Daily Precipitation:** {avg_precip:.2f} mm/day")
    st.markdown(f"**Average Maximum Temperature:** {avg_max_temp:.2f} °C")

    # Assess crop quality.
    rating, overall_score, _, _ = assess_date_crop_quality(climate_df)
    st.markdown(f"**Predicted Date Crop Quality:** {rating} (Score: {overall_score:.2f})")

    # Allow user to set a threshold for acceptable quality.
    quality_levels = {"EXCELLENT": 5, "VERY GOOD": 4, "GOOD": 3, "MODERATE": 2, "BAD": 1}
    default_threshold = 3  # "GOOD" or better is acceptable.
    threshold_level = st.slider("Set Minimum Acceptable Crop Quality Level (1=BAD, 5=EXCELLENT)", min_value=1, max_value=5, value=default_threshold, step=1)
    predicted_level = quality_levels.get(rating, 3)
    if predicted_level < threshold_level:
        st.error("🚨 Alert: Forecasted crop quality is below the acceptable threshold! Consider reviewing irrigation and crop management practices.")
    else:
        st.success("✅ Forecasted crop quality meets the acceptable threshold.")

    st.success("✅ Date Crop Analysis Dashboard loaded successfully!")

if __name__ == "__main__":
    date_crop_analysis_dashboard()
