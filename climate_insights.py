import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# -------------------------------------------------------------------
# Helper: Simulate historical climate data (rainfall in mm and temperature in °C)
# for a given country from 2012 to the present (monthly frequency).
# In practice, you would replace this with real climate data.
# -------------------------------------------------------------------
def simulate_climate_data(country: str):
    # Generate a date range from Jan 2012 to current month
    start = datetime(2012, 1, 1)
    end = datetime.today().replace(day=1)
    periods = pd.date_range(start, end, freq='MS')
    n = len(periods)
    
    # For simulation, assign different base conditions per country
    # (These base values are illustrative.)
    climate_params = {
        "IRAQ": {"rainfall_base": 20, "temp_base": 35},
        "UAE": {"rainfall_base": 15, "temp_base": 38},
        "IRAN": {"rainfall_base": 25, "temp_base": 34},
        "SAUDI ARABIA": {"rainfall_base": 10, "temp_base": 40},
        "TUNISIA": {"rainfall_base": 50, "temp_base": 30},
        "ALGERIA": {"rainfall_base": 45, "temp_base": 32},
        "ISRAEL": {"rainfall_base": 60, "temp_base": 28},
        "JORDAN": {"rainfall_base": 55, "temp_base": 29},
        "STATE OF PALESTINE": {"rainfall_base": 60, "temp_base": 28},
    }
    # Use uppercase keys for matching
    country_key = country.upper()
    params = climate_params.get(country_key, {"rainfall_base": 40, "temp_base": 30})
    
    # Simulate monthly rainfall and temperature with some random noise
    np.random.seed(42)
    rainfall = np.clip(np.random.normal(loc=params["rainfall_base"], scale=10, size=n), 0, None)
    temperature = np.random.normal(loc=params["temp_base"], scale=3, size=n)
    
    df = pd.DataFrame({
        "Period": periods,
        "Rainfall": rainfall,
        "Temperature": temperature
    })
    df["Period_str"] = df["Period"].dt.strftime("%b-%Y")
    return df

# -------------------------------------------------------------------
# Helper: Classify the crop outcome based on rainfall and temperature.
# These rules are illustrative. Adjust thresholds and categories as needed.
# -------------------------------------------------------------------
def classify_crop_yield(rainfall, temperature):
    # Example rules:
    # - Excellent: Rainfall between 40 and 80 mm AND temperature between 25-32°C.
    # - Very Good: Rainfall between 30 and 40 mm or 80-90 mm; temperature close to ideal.
    # - Good: Rainfall between 20 and 30 mm or 90-100 mm; moderate temperatures.
    # - Moderate: Rainfall slightly out of ideal range.
    # - Poor: Very low rainfall (<20 mm) or very high (>100 mm), or extreme temperatures.
    
    if 40 <= rainfall <= 80 and 25 <= temperature <= 32:
        return "Excellent"
    elif (30 <= rainfall < 40 or 80 < rainfall <= 90) and 24 <= temperature <= 33:
        return "Very Good"
    elif (20 <= rainfall < 30 or 90 < rainfall <= 100) and 23 <= temperature <= 34:
        return "Good"
    elif (rainfall < 20 or rainfall > 100) or (temperature < 20 or temperature > 36):
        return "Poor"
    else:
        return "Moderate"

# -------------------------------------------------------------------
# Main Dashboard Function for Climate Insights (Date Crop Review)
# -------------------------------------------------------------------
def yearly_crop_review_dashboard(data: pd.DataFrame):
    st.title("🌦 Advanced Climate & Crop Review for Date Cultivation")
    st.markdown("""
    This dashboard estimates date crop performance based on simulated climate conditions (rainfall and temperature) 
    for key partner countries where dates are grown. Adjust the parameters to see how conditions over time may affect 
    crop quality.
    """)
    
    # Allow user to select the partner country of interest.
    partners = ["Iraq", "UAE", "Iran", "Saudi Arabia", "Tunisia", "Algeria", "Israel", "Jordan", "State of Palestine"]
    selected_country = st.selectbox("Select Country (Partner):", partners)
    
    # Get simulated climate data for the selected country.
    climate_df = simulate_climate_data(selected_country)
    
    # Let user optionally adjust ideal thresholds via sidebar.
    st.sidebar.header("Adjust Ideal Conditions")
    ideal_rainfall_min = st.sidebar.number_input("Ideal Rainfall Min (mm)", value=40.0, step=1.0)
    ideal_rainfall_max = st.sidebar.number_input("Ideal Rainfall Max (mm)", value=80.0, step=1.0)
    ideal_temp_min = st.sidebar.number_input("Ideal Temperature Min (°C)", value=25.0, step=0.5)
    ideal_temp_max = st.sidebar.number_input("Ideal Temperature Max (°C)", value=32.0, step=0.5)
    
    # Classify crop outcome for each month based on the ideal thresholds.
    climate_df["Crop Outcome"] = climate_df.apply(
        lambda row: (
            "Excellent" if ideal_rainfall_min <= row["Rainfall"] <= ideal_rainfall_max and ideal_temp_min <= row["Temperature"] <= ideal_temp_max
            else "Poor" if row["Rainfall"] < ideal_rainfall_min or row["Rainfall"] > (ideal_rainfall_max + 20) or row["Temperature"] < (ideal_temp_min - 3) or row["Temperature"] > (ideal_temp_max + 3)
            else "Moderate"
        ), axis=1
    )
    
    # Summary by Year: average rainfall, temperature, and dominant crop outcome.
    climate_df["Year"] = climate_df["Period"].dt.year
    yearly_summary = climate_df.groupby("Year").agg({
        "Rainfall": "mean",
        "Temperature": "mean",
        "Crop Outcome": lambda x: x.mode()[0] if not x.mode().empty else "N/A"
    }).reset_index()
    yearly_summary.rename(columns={
        "Rainfall": "Avg Rainfall (mm)",
        "Temperature": "Avg Temp (°C)",
        "Crop Outcome": "Dominant Outcome"
    }, inplace=True)
    
    # Multi-tab layout
    tabs = st.tabs(["Overview", "Monthly Trends", "Yearly Review", "Download Data"])
    
    #########################################################
    # Tab 1: Overview – Automated Insights and Data Table
    #########################################################
    with tabs[0]:
        st.header(f"Climate Overview for {selected_country}")
        st.markdown("#### Automated Insights")
        insights = []
        for year in sorted(yearly_summary["Year"].unique()):
            row = yearly_summary[yearly_summary["Year"] == year].iloc[0]
            insights.append(f"**{year}**: Avg Rainfall = {row['Avg Rainfall (mm)']:.1f} mm, Avg Temp = {row['Avg Temp (°C)']:.1f}°C, Crop Outcome: **{row['Dominant Outcome']}**.")
        st.markdown("\n\n".join(insights))
        st.markdown("#### Detailed Climate Data")
        st.dataframe(climate_df[["Period_str", "Rainfall", "Temperature", "Crop Outcome"]])
    
    #########################################################
    # Tab 2: Monthly Trends – Line Charts
    #########################################################
    with tabs[1]:
        st.header("Monthly Climate Trends")
        fig_rain = px.line(climate_df, x="Period_str", y="Rainfall", title="Monthly Rainfall Trend (mm)", markers=True, template="plotly_white")
        fig_temp = px.line(climate_df, x="Period_str", y="Temperature", title="Monthly Temperature Trend (°C)", markers=True, template="plotly_white")
        st.plotly_chart(fig_rain, use_container_width=True)
        st.plotly_chart(fig_temp, use_container_width=True)
    
    #########################################################
    # Tab 3: Yearly Review – Grouped Bar Chart by Year and Outcome
    #########################################################
    with tabs[2]:
        st.header("Yearly Crop Outcome Review")
        outcome_year = climate_df.groupby(["Year", "Crop Outcome"]).size().reset_index(name="Count")
        fig_outcome = px.bar(outcome_year, x="Year", y="Count", color="Crop Outcome",
                             title="Yearly Distribution of Crop Outcomes", barmode="stack", template="plotly_white")
        st.plotly_chart(fig_outcome, use_container_width=True)
    
    #########################################################
    # Tab 4: Download Data
    #########################################################
    with tabs[3]:
        st.header("Download Climate Data")
        csv_data = climate_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download as CSV", csv_data, "climate_data.csv", "text/csv")
    
    st.success("✅ Climate Insights Dashboard loaded successfully!")

# For testing standalone, uncomment the following:
# if __name__ == "__main__":
#     # Simulate a minimal DataFrame (your main data should already be preprocessed)
#     dummy_df = pd.DataFrame({
#         "Year": [2012]*5,
#         "Month": [1, 2, 3, 4, 5],
#         "Reporter": ["India"]*5,
#         "Flow": ["Import"]*5,
#         "Partner": ["Iraq", "UAE", "Iran", "Saudi Arabia", "Tunisia"],
#         "Code": [804]*5,
#         "Desc": ["Dates"]*5,
#         "Tons": [100, 200, 150, 250, 300]
#     })
#     yearly_crop_review_dashboard(dummy_df)
