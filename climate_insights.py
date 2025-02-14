import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go

# -------------------------------------------------------------------
# Helper function: Simulate monthly climate data for a specific region in Saudi Arabia.
# You can replace this simulation with real data from an API or CSV.
# -------------------------------------------------------------------
def simulate_climate_data(region: str):
    # Define the simulation parameters for each region.
    # These parameters are illustrative; adjust the base values and noise as needed.
    region_params = {
        "Al-Qassim": {"rainfall_base": 15, "temp_base": 38},
        "Al-Madinah": {"rainfall_base": 10, "temp_base": 40},
        "Riyadh": {"rainfall_base": 12, "temp_base": 39},
        "Eastern Province": {"rainfall_base": 20, "temp_base": 36},
    }
    if region not in region_params:
        st.error(f"Region {region} not recognized.")
        return pd.DataFrame()

    params = region_params[region]
    
    # Create a monthly date range from January 2012 to current month.
    start_date = datetime(2012, 1, 1)
    end_date = datetime.today().replace(day=1)
    periods = pd.date_range(start_date, end_date, freq="MS")
    n = len(periods)
    
    # Simulate monthly rainfall (in mm) and temperature (in °C) with some random noise.
    # Rainfall is clipped to nonnegative values.
    np.random.seed(42)
    rainfall = np.clip(np.random.normal(loc=params["rainfall_base"], scale=5, size=n), 0, None)
    temperature = np.random.normal(loc=params["temp_base"], scale=2, size=n)
    
    df = pd.DataFrame({
        "Period": periods,
        "Rainfall": rainfall,
        "Temperature": temperature
    })
    df["Period_str"] = df["Period"].dt.strftime("%b-%Y")
    return df

# -------------------------------------------------------------------
# Helper function: Classify crop outcome based on rainfall and temperature.
# Adjust the thresholds as per expert knowledge about date cultivation.
# -------------------------------------------------------------------
def classify_crop_outcome(row, ideal_rain_min, ideal_rain_max, ideal_temp_min, ideal_temp_max):
    # Ideal conditions yield "Excellent" outcomes.
    if ideal_rain_min <= row["Rainfall"] <= ideal_rain_max and ideal_temp_min <= row["Temperature"] <= ideal_temp_max:
        return "Excellent"
    # If conditions are moderately off, classify as "Good" or "Moderate"
    elif (ideal_rain_min * 0.8 <= row["Rainfall"] < ideal_rain_min) or (ideal_rain_max < row["Rainfall"] <= ideal_rain_max * 1.2):
        if ideal_temp_min - 2 <= row["Temperature"] <= ideal_temp_max + 2:
            return "Good"
        else:
            return "Moderate"
    # Extreme deviations yield "Poor"
    else:
        return "Poor"

# -------------------------------------------------------------------
# Main Dashboard Function for Climate Insights (Saudi Arabia – Date Crop Review)
# -------------------------------------------------------------------
def yearly_crop_review_dashboard(data: pd.DataFrame):
    st.title("🌦 Saudi Arabia Date Crop Climate Insights")
    st.markdown("""
    This dashboard reviews simulated climate conditions (rainfall and temperature) for key date‐growing regions in Saudi Arabia.  
    Select a region to see monthly climate trends, review yearly crop outcome summaries, and download the climate data.
    """)

    # Let the user select the region of interest.
    regions = ["Al-Qassim", "Al-Madinah", "Riyadh", "Eastern Province"]
    selected_region = st.selectbox("Select Region:", regions)

    # Load (simulate) the climate data for the selected region.
    climate_df = simulate_climate_data(selected_region)
    if climate_df.empty:
        st.error("No climate data available.")
        return

    # Sidebar: Allow adjustment of ideal thresholds for an "ideal" crop outcome.
    st.sidebar.header("Ideal Climate Conditions")
    ideal_rain_min = st.sidebar.number_input("Ideal Rainfall Minimum (mm)", value=15.0, step=0.5)
    ideal_rain_max = st.sidebar.number_input("Ideal Rainfall Maximum (mm)", value=25.0, step=0.5)
    ideal_temp_min = st.sidebar.number_input("Ideal Temperature Minimum (°C)", value=35.0, step=0.5)
    ideal_temp_max = st.sidebar.number_input("Ideal Temperature Maximum (°C)", value=40.0, step=0.5)

    # Classify crop outcome for each month using the provided thresholds.
    climate_df["Crop Outcome"] = climate_df.apply(
        lambda row: classify_crop_outcome(row, ideal_rain_min, ideal_rain_max, ideal_temp_min, ideal_temp_max),
        axis=1
    )

    # Create a Year column for aggregation.
    climate_df["Year"] = climate_df["Period"].dt.year

    # Generate a yearly summary: average rainfall, average temperature, and most frequent crop outcome.
    yearly_summary = climate_df.groupby("Year").agg({
        "Rainfall": "mean",
        "Temperature": "mean",
        "Crop Outcome": lambda outcomes: outcomes.mode()[0] if not outcomes.mode().empty else "N/A"
    }).reset_index()
    yearly_summary.rename(columns={
        "Rainfall": "Avg Rainfall (mm)",
        "Temperature": "Avg Temp (°C)",
        "Crop Outcome": "Dominant Outcome"
    }, inplace=True)

    # Multi-tab layout for the module.
    tabs = st.tabs(["Overview", "Monthly Trends", "Yearly Review", "Download Data"])

    #########################################################
    # Tab 1: Overview – Automated Insights and Data Table
    #########################################################
    with tabs[0]:
        st.header(f"Climate Overview for {selected_region}")
        st.markdown("#### Automated Insights")
        insights = []
        for year in sorted(yearly_summary["Year"].unique()):
            row = yearly_summary[yearly_summary["Year"] == year].iloc[0]
            insights.append(f"**{year}**: Avg Rainfall = {row['Avg Rainfall (mm)']:.1f} mm, Avg Temp = {row['Avg Temp (°C)']:.1f}°C, Dominant Crop Outcome: **{row['Dominant Outcome']}**.")
        st.markdown("\n\n".join(insights))
        st.markdown("#### Detailed Monthly Climate Data")
        st.dataframe(climate_df[["Period_str", "Rainfall", "Temperature", "Crop Outcome"]])

    #########################################################
    # Tab 2: Monthly Trends – Line Charts for Rainfall and Temperature
    #########################################################
    with tabs[1]:
        st.header("Monthly Climate Trends")
        fig_rain = px.line(climate_df, x="Period_str", y="Rainfall", title="Monthly Rainfall Trend (mm)", markers=True, template="plotly_white")
        fig_temp = px.line(climate_df, x="Period_str", y="Temperature", title="Monthly Temperature Trend (°C)", markers=True, template="plotly_white")
        st.plotly_chart(fig_rain, use_container_width=True)
        st.plotly_chart(fig_temp, use_container_width=True)

    #########################################################
    # Tab 3: Yearly Review – Stacked Bar Chart of Crop Outcomes by Year
    #########################################################
    with tabs[2]:
        st.header("Yearly Crop Outcome Review")
        outcome_year = climate_df.groupby(["Year", "Crop Outcome"]).size().reset_index(name="Count")
        fig_outcome = px.bar(
            outcome_year, 
            x="Year", 
            y="Count", 
            color="Crop Outcome",
            title="Yearly Distribution of Crop Outcomes",
            barmode="stack",
            template="plotly_white"
        )
        st.plotly_chart(fig_outcome, use_container_width=True)
        st.markdown("#### Yearly Climate Summary Table")
        st.dataframe(yearly_summary)

    #########################################################
    # Tab 4: Download Data
    #########################################################
    with tabs[3]:
        st.header("Download Climate Data")
        csv_data = climate_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download as CSV", csv_data, "climate_data.csv", "text/csv")

    st.success("✅ Saudi Arabia Climate Insights Dashboard loaded successfully!")

# For standalone testing uncomment below:
# if __name__ == "__main__":
#     yearly_crop_review_dashboard(pd.DataFrame())  # Replace with actual data if testing.
