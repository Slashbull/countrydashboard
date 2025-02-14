import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from prophet import Prophet

# -------------------------------------------------------------------
# Helper: Simulate monthly climate data for a selected Saudi region.
# (Replace this simulation with real API or CSV data as available.)
# -------------------------------------------------------------------
def simulate_climate_data(region: str) -> pd.DataFrame:
    # Parameters for each region (example values – adjust as needed)
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
    start_date = datetime(2012, 1, 1)
    end_date = datetime.today().replace(day=1)
    periods = pd.date_range(start_date, end_date, freq="MS")
    n = len(periods)
    np.random.seed(42)
    # Simulate rainfall (mm) and temperature (°C)
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
# Helper: Compute a crop score and classify crop outcome.
# You can adjust thresholds based on agronomic expertise.
# -------------------------------------------------------------------
def compute_crop_outcome(row) -> str:
    # Define thresholds (example values)
    # For an "Excellent" crop, ideal rainfall between 15 and 25 mm and temperature between 35 and 40°C.
    ideal_rain_min, ideal_rain_max = 15, 25
    ideal_temp_min, ideal_temp_max = 35, 40

    # For "Good": a moderate deviation (rainfall between 12-15 or 25-30, and temperature within ±2°C).
    # "Moderate": mild deviations; "Poor": extreme conditions.
    rain = row["Rainfall"]
    temp = row["Temperature"]

    # Score rainfall deviation (0 means perfect; higher means worse)
    if ideal_rain_min <= rain <= ideal_rain_max:
        rain_score = 0
    elif rain < ideal_rain_min:
        rain_score = (ideal_rain_min - rain) / ideal_rain_min
    else:
        rain_score = (rain - ideal_rain_max) / ideal_rain_max

    # Score temperature deviation similarly.
    if ideal_temp_min <= temp <= ideal_temp_max:
        temp_score = 0
    elif temp < ideal_temp_min:
        temp_score = (ideal_temp_min - temp) / ideal_temp_min
    else:
        temp_score = (temp - ideal_temp_max) / ideal_temp_max

    # Combine scores (you may weight these differently)
    score = (rain_score + temp_score) / 2

    # Map score to outcome:
    # 0 - 0.1: Excellent, 0.1 - 0.25: Good, 0.25 - 0.5: Moderate, >0.5: Poor
    if score <= 0.1:
        return "Excellent"
    elif score <= 0.25:
        return "Good"
    elif score <= 0.5:
        return "Moderate"
    else:
        return "Poor"

# -------------------------------------------------------------------
# Helper: Forecast future climate conditions using Prophet.
# -------------------------------------------------------------------
def forecast_climate(df: pd.DataFrame, metric: str, periods: int = 12) -> pd.DataFrame:
    forecast_df = df[["Period", metric]].rename(columns={"Period": "ds", metric: "y"})
    m = Prophet()
    m.fit(forecast_df)
    future = m.make_future_dataframe(periods=periods, freq="MS")
    forecast = m.predict(future)
    return forecast

# -------------------------------------------------------------------
# Main Dashboard Function: Yearly Crop Review & Climate Insights
# -------------------------------------------------------------------
def yearly_crop_review_dashboard(data: pd.DataFrame):
    st.title("🌦 Saudi Arabia Date Crop Climate Insights")
    st.markdown("""
    This dashboard reviews the simulated climate conditions for a selected Saudi region and assesses their impact on date crop quality.  
    Adjust the ideal climate thresholds and review monthly trends as well as yearly crop outcome summaries.
    """)

    # Let user select a region.
    regions = ["Al-Qassim", "Al-Madinah", "Riyadh", "Eastern Province"]
    selected_region = st.selectbox("Select Region:", regions)

    # Simulate climate data.
    climate_df = simulate_climate_data(selected_region)
    if climate_df.empty:
        st.error("No climate data available.")
        return

    # Sidebar: Allow adjustment of ideal climate conditions.
    st.sidebar.header("Adjust Ideal Conditions")
    ideal_rain_min = st.sidebar.number_input("Ideal Rainfall Minimum (mm)", value=15.0, step=0.5)
    ideal_rain_max = st.sidebar.number_input("Ideal Rainfall Maximum (mm)", value=25.0, step=0.5)
    ideal_temp_min = st.sidebar.number_input("Ideal Temperature Minimum (°C)", value=35.0, step=0.5)
    ideal_temp_max = st.sidebar.number_input("Ideal Temperature Maximum (°C)", value=40.0, step=0.5)

    # Classify each month’s crop outcome.
    climate_df["Crop Outcome"] = climate_df.apply(compute_crop_outcome, axis=1)

    # Add Year column.
    climate_df["Year"] = climate_df["Period"].dt.year

    # Compute yearly summary: average rainfall, average temperature, and dominant outcome (mode).
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

    # Create multi-tab layout.
    tabs = st.tabs(["Overview", "Monthly Trends", "Yearly Review", "Forecast", "Download Data"])

    #########################################################
    # Tab 1: Overview – Automated Insights and Data Table
    #########################################################
    with tabs[0]:
        st.header(f"Overview for {selected_region}")
        insights = []
        for year in sorted(yearly_summary["Year"].unique()):
            row = yearly_summary[yearly_summary["Year"] == year].iloc[0]
            insights.append(f"**{year}**: Avg Rainfall = {row['Avg Rainfall (mm)']:.1f} mm, Avg Temp = {row['Avg Temp (°C)']:.1f}°C, Dominant Outcome: **{row['Dominant Outcome']}**.")
        st.markdown("\n\n".join(insights))
        st.markdown("#### Detailed Monthly Climate Data")
        st.dataframe(climate_df[["Period_str", "Rainfall", "Temperature", "Crop Outcome"]])

    #########################################################
    # Tab 2: Monthly Trends – Line Charts
    #########################################################
    with tabs[1]:
        st.header("Monthly Climate Trends")
        fig1 = px.line(climate_df, x="Period_str", y="Rainfall", title="Monthly Rainfall Trend (mm)", markers=True, template="plotly_white")
        fig2 = px.line(climate_df, x="Period_str", y="Temperature", title="Monthly Temperature Trend (°C)", markers=True, template="plotly_white")
        # Add annotations (for example, highlight months with "Poor" outcomes)
        poor_months = climate_df[climate_df["Crop Outcome"]=="Poor"]
        for idx, row in poor_months.iterrows():
            fig1.add_annotation(x=row["Period_str"], y=row["Rainfall"],
                                text="Poor", showarrow=True, arrowhead=1, ax=0, ay=-30)
            fig2.add_annotation(x=row["Period_str"], y=row["Temperature"],
                                text="Poor", showarrow=True, arrowhead=1, ax=0, ay=-30)
        st.plotly_chart(fig1, use_container_width=True)
        st.plotly_chart(fig2, use_container_width=True)

    #########################################################
    # Tab 3: Yearly Review – Stacked Bar Chart of Crop Outcomes by Year
    #########################################################
    with tabs[2]:
        st.header("Yearly Crop Outcome Review")
        outcome_year = climate_df.groupby(["Year", "Crop Outcome"]).size().reset_index(name="Count")
        fig_year = px.bar(
            outcome_year, 
            x="Year", 
            y="Count", 
            color="Crop Outcome",
            title="Yearly Distribution of Crop Outcomes",
            barmode="stack",
            template="plotly_white"
        )
        st.plotly_chart(fig_year, use_container_width=True)
        st.markdown("#### Yearly Climate Summary")
        st.dataframe(yearly_summary)

    #########################################################
    # Tab 4: Forecast – Future Climate Prediction Using Prophet
    #########################################################
    with tabs[3]:
        st.header("Climate Forecasting")
        forecast_metric = st.selectbox("Select Metric to Forecast:", ["Rainfall", "Temperature"])
        st.markdown("Forecasting the future 12 months using Prophet.")
        forecast_df = forecast_climate(climate_df, forecast_metric, periods=12)
        fig_forecast = go.Figure()
        fig_forecast.add_trace(go.Scatter(x=climate_df["Period_str"], y=climate_df[forecast_metric],
                                          mode="markers+lines", name="Historical"))
        # Format forecast dates as strings matching our x-axis
        forecast_dates = forecast_df["ds"].dt.strftime("%b-%Y")
        fig_forecast.add_trace(go.Scatter(x=forecast_dates, y=forecast_df["yhat"],
                                          mode="lines+markers", name="Forecast",
                                          line=dict(dash="dash", color="red")))
        fig_forecast.update_layout(
            title=f"{forecast_metric} Forecast for {selected_region}",
            xaxis_title="Period",
            yaxis_title=forecast_metric,
            template="plotly_white"
        )
        st.plotly_chart(fig_forecast, use_container_width=True)

    #########################################################
    # Tab 5: Download Data
    #########################################################
    with tabs[4]:
        st.header("Download Climate Data")
        csv_data = climate_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download as CSV", csv_data, "climate_data.csv", "text/csv")

    st.success("✅ Saudi Arabia Climate Insights Dashboard loaded successfully!")

# For standalone testing, uncomment below:
# if __name__ == "__main__":
#     yearly_crop_review_dashboard(pd.DataFrame())
