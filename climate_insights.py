# climate_insights.py
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime
from config import WEATHER_API_KEY

# -------------------------
# API FETCH FUNCTIONS
# -------------------------
def fetch_open_meteo_data(latitude, longitude, start_date, end_date):
    """
    Fetch historical weather data from the free Open-Meteo Archive API.
    Returns JSON data containing daily max temperature and precipitation.
    """
    base_url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_max,precipitation_sum",
        "timezone": "auto"
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    return response.json()

def fetch_openweather_data(latitude, longitude, date_str):
    """
    Fetch weather data from OpenWeather's historical (timemachine) API.
    Note: OpenWeather’s historical API only allows one day per call.
    This function fetches data for the given date.
    """
    # Convert date to Unix timestamp.
    dt = int(datetime.strptime(date_str, "%Y-%m-%d").timestamp())
    base_url = "http://api.openweathermap.org/data/2.5/onecall/timemachine"
    params = {
        "lat": latitude,
        "lon": longitude,
        "dt": dt,
        "appid": WEATHER_API_KEY,
        "units": "metric"
    }
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    return response.json()

# -------------------------
# DATA PROCESSING FUNCTIONS
# -------------------------
def analyze_open_meteo_data(data):
    """
    Process Open-Meteo JSON data to compute daily averages.
    Returns a DataFrame with 'time', 'temperature_2m_max', and 'precipitation_sum'.
    """
    daily = data.get("daily", {})
    if not daily:
        st.error("No daily data returned from the weather API.")
        return pd.DataFrame()
    df = pd.DataFrame({
        "date": pd.to_datetime(daily.get("time", [])),
        "max_temp": daily.get("temperature_2m_max", []),
        "rainfall": daily.get("precipitation_sum", [])
    })
    df["year"] = df["date"].dt.year
    return df

def analyze_openweather_data(data):
    """
    Process OpenWeather JSON data.
    OpenWeather returns hourly data. We aggregate to get the max temperature and total rainfall for that day.
    """
    hourly = data.get("hourly", [])
    if not hourly:
        st.error("No hourly data returned from the weather API.")
        return pd.DataFrame()
    df = pd.DataFrame(hourly)
    df["date"] = pd.to_datetime(df["dt"], unit="s")
    # Get max temperature and sum of rainfall (if available) for the day.
    # Rain may be nested under 'rain' (e.g., {"1h": value})
    df["rainfall"] = df.get("rain", pd.Series([0]*len(df))).apply(lambda x: x.get("1h", 0) if isinstance(x, dict) else 0)
    summary = df.groupby(df["date"].dt.date).agg({
        "temp": "max",
        "rainfall": "sum"
    }).reset_index().rename(columns={"date": "date", "temp": "max_temp"})
    summary["date"] = pd.to_datetime(summary["date"])
    summary["year"] = summary["date"].dt.year
    return summary

def classify_crop_outcome(avg_rainfall, avg_temp):
    """
    Given average rainfall (in mm) and average maximum temperature (°C),
    classify the crop outcome for dates. The thresholds below are hypothetical;
    you should calibrate them based on agronomic research.
    """
    # Optimal conditions for date palms (example values):
    # Rainfall: ~14-16 mm, Max Temp: ~37-39°C → Excellent
    if 13 <= avg_rainfall <= 17 and 37 <= avg_temp <= 39:
        return "Excellent"
    elif (11 <= avg_rainfall < 13 or 17 < avg_rainfall <= 19) or (36 <= avg_temp < 37 or 39 < avg_temp <= 40):
        return "Good"
    elif (9 <= avg_rainfall < 11 or 19 < avg_rainfall <= 21) or (35 <= avg_temp < 36 or 40 < avg_temp <= 41):
        return "Moderate"
    else:
        return "Poor"

# -------------------------
# DASHBOARD FUNCTION
# -------------------------
def yearly_crop_review_dashboard(data: pd.DataFrame):
    st.title("🌦 Climate & Date Crop Outcome Insights")
    st.markdown("""
    This module fetches historical weather data for a selected country/region, aggregates it by year,
    and predicts the dominant crop outcome (for dates) based on average rainfall and maximum temperature.
    """)
    
    # Let user select the country (representative region for date cultivation)
    countries = ["Iraq", "United Arab Emirates", "Iran", "Saudi Arabia", "Tunisia", "Algeria", "Israel", "Jordan", "State of Palestine"]
    selected_country = st.selectbox("Select Country:", countries)
    
    # Representative coordinates for date growing regions:
    coordinates = {
        "Iraq": (30.5085, 47.7836),  # Basra region
        "United Arab Emirates": (24.2075, 55.7447),  # Al Ain region
        "Iran": (29.5918, 52.5836),  # Khuzestan region
        "Saudi Arabia": (26.33, 43.97),  # Al-Qassim region (approx)
        "Tunisia": (33.9190, 8.1303),  # Tozeur region
        "Algeria": (34.8554, 5.7280),  # Biskra region
        "Israel": (31.0461, 34.8516),  # Jordan Valley area (approx)
        "Jordan": (31.9454, 35.9284),  # Jordan Valley
        "State of Palestine": (31.9468, 35.3027)  # Jericho area
    }
    lat, lon = coordinates[selected_country]
    
    # Let user choose which weather API to use.
    api_method = st.radio("Select Weather API:", ["Open-Meteo (Free)", "OpenWeather (Using API Key)"])
    
    # Let user specify the year range for analysis.
    current_year = datetime.now().year
    start_year = st.number_input("Start Year:", min_value=2012, max_value=current_year, value=2012, step=1)
    end_year = st.number_input("End Year:", min_value=2012, max_value=current_year, value=current_year, step=1)
    if start_year > end_year:
        st.error("Start Year must be less than or equal to End Year.")
        return
    
    start_date = f"{start_year}-01-01"
    end_date = f"{end_year}-12-31"
    
    st.info(f"Fetching weather data for {selected_country} from {start_date} to {end_date} using {api_method}...")
    
    # Fetch data from the chosen API
    weather_json = None
    try:
        if api_method == "Open-Meteo (Free)":
            weather_json = fetch_open_meteo_data(lat, lon, start_date, end_date)
            df_weather = analyze_open_meteo_data(weather_json)
        else:
            # For OpenWeather, we'll demonstrate with a single day's data per year.
            # In production, you might loop over each year and average the values.
            years = list(range(start_year, end_year + 1))
            records = []
            for yr in years:
                sample_date = f"{yr}-06-15"  # choose mid-year as representative
                try:
                    json_data = fetch_openweather_data(lat, lon, sample_date)
                    df_day = analyze_openweather_data(json_data)
                    if not df_day.empty:
                        # Average the day's values (only one day, so it's the value)
                        records.append({"year": yr,
                                        "rainfall": df_day["rainfall"].mean(),
                                        "max_temp": df_day["max_temp"].mean()})
                except Exception as e:
                    st.error(f"Error fetching OpenWeather data for {yr}: {e}")
            df_weather = pd.DataFrame(records)
    except Exception as e:
        st.error(f"Error fetching weather data: {e}")
        return
    
    if df_weather.empty:
        st.error("No weather data available.")
        return
    
    # Compute crop outcome per year
    df_weather["Crop Outcome"] = df_weather.apply(lambda row: classify_crop_outcome(row["rainfall"], row["max_temp"]), axis=1)
    
    # Display the yearly summary
    st.subheader("Yearly Climate & Crop Outcome Summary")
    st.dataframe(df_weather)
    
    # Plot trends
    fig_temp = px.line(df_weather, x="year", y="max_temp", title="Yearly Avg Max Temperature (°C)", markers=True)
    fig_rain = px.line(df_weather, x="year", y="rainfall", title="Yearly Avg Rainfall (mm)", markers=True)
    st.plotly_chart(fig_temp, use_container_width=True)
    st.plotly_chart(fig_rain, use_container_width=True)
    
    st.markdown("### Combined Climate & Outcome Insights")
    for _, row in df_weather.iterrows():
        st.write(f"{int(row['year'])}: Avg Rainfall = {row['rainfall']:.1f} mm, Avg Max Temp = {row['max_temp']:.1f} °C, Dominant Outcome: {row['Crop Outcome']}")
    
    st.success("✅ Climate Insights Dashboard loaded successfully!")
    
if __name__ == "__main__":
    yearly_crop_review_dashboard(None)  # For testing standalone; remove or integrate in core_system.py in production.
