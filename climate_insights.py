import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from prophet import Prophet
from datetime import datetime

# =============================================================================
# Helper: Simulate monthly climate data for a selected region
# (Replace this simulation with real climate data when available)
# =============================================================================
def simulate_climate_data(region: str) -> pd.DataFrame:
    # For demonstration, we simulate data for Saudi Arabia’s key date‐growing regions.
    # You can adjust these base values according to expert data.
    region_params = {
        "Al-Qassim": {"rainfall_base": 16.5, "temp_base": 38.5},
        "Al-Madinah": {"rainfall_base": 12.0, "temp_base": 38.6},
        "Riyadh": {"rainfall_base": 14.0, "temp_base": 37.6},
        "Eastern Province": {"rainfall_base": 15.2, "temp_base": 39.4},
    }
    if region not in region_params:
        st.error(f"Region '{region}' is not recognized.")
        return pd.DataFrame()
    params = region_params[region]
    start_date = datetime(2012, 1, 1)
    # For a complete review, we simulate data until the current month.
    end_date = datetime.today().replace(day=1)
    periods = pd.date_range(start_date, end_date, freq="MS")
    n = len(periods)
    np.random.seed(42)
    # Simulate rainfall (mm) and temperature (°C) with some variability.
    rainfall = np.clip(np.random.normal(loc=params["rainfall_base"], scale=2, size=n), 0, None)
    temperature = np.random.normal(loc=params["temp_base"], scale=1.5, size=n)
    df = pd.DataFrame({
        "Period": periods,
        "Rainfall": rainfall,
        "Temperature": temperature
    })
    df["Period_str"] = df["Period"].dt.strftime("%b-%Y")
    return df

# =============================================================================
# Helper: Compute crop outcome based on rainfall and temperature.
# =============================================================================
def compute_crop_outcome(row, ideal_rain_min, ideal_rain_max, ideal_temp_min, ideal_temp_max) -> str:
    rain = row["Rainfall"]
    temp = row["Temperature"]
    # Compute deviation scores for rainfall and temperature.
    if ideal_rain_min <= rain <= ideal_rain_max:
        rain_score = 0
    elif rain < ideal_rain_min:
        rain_score = (ideal_rain_min - rain) / ideal_rain_min
    else:
        rain_score = (rain - ideal_rain_max) / ideal_rain_max

    if ideal_temp_min <= temp <= ideal_temp_max:
        temp_score = 0
    elif temp < ideal_temp_min:
        temp_score = (ideal_temp_min - temp) / ideal_temp_min
    else:
        temp_score = (temp - ideal_temp_max) / ideal_temp_max

    # Combine scores equally.
    score = (rain_score + temp_score) / 2
    # Map the combined score to an outcome.
    if score <= 0.1:
        return "Excellent"
    elif score <= 0.25:
        return "Good"
    elif score <= 0.5:
        return "Moderate"
    else:
        return "Poor"

# =============================================================================
# Helper: Forecast future climate metric using Prophet.
# =============================================================================
def forecast_climate(df: pd.DataFrame, metric: str, periods: int = 12) -> pd.DataFrame:
    forecast_df = df[["Period", metric]].rename(columns={"Period": "ds", metric: "y"})
    model = Prophet()
    model.fit(forecast_df)
    future = model.make_future_dataframe(periods=periods, freq="MS")
    forecast = model.predict(future)
    return forecast

# =============================================================================
# Main Dashboard Function: Yearly Crop Review & Climate Insights
# =============================================================================
def yearly_crop_review_dashboard(data: pd.DataFrame):
    st.title("🌦 Date Crop Climate Insights for Saudi Arabia")
    st.markdown("""
    This dashboard evaluates the climate conditions affecting date crop quality in key regions of Saudi Arabia.
    The ideal climate for date cultivation typically includes:
    
    - **Rainfall:** Moderate (e.g., 14–20 mm/month)
    - **Temperature:** Warm (e.g., 35–40°C)
    
    Adjust the ideal conditions in the sidebar to see how historical climate compares—and forecast future trends.
    """)

    # Let the user select a region.
    regions = ["Al-Qassim", "Al-Madinah", "Riyadh", "Eastern Province"]
    selected_region = st.selectbox("Select Region:", regions)

    # Simulate climate data.
    climate_df = simulate_climate_data(selected_region)
    if climate_df.empty:
        st.error("No climate data available.")
        return

    # Sidebar: Allow adjustments to ideal conditions.
    st.sidebar.header("Ideal Conditions for Dates")
    ideal_rain_min = st.sidebar.number_input("Ideal Rainfall Minimum (mm)", value=14.0, step=0.5)
    ideal_rain_max = st.sidebar.number_input("Ideal Rainfall Maximum (mm)", value=20.0, step=0.5)
    ideal_temp_min = st.sidebar.number_input("Ideal Temperature Minimum (°C)", value=35.0, step=0.5)
    ideal_temp_max = st.sidebar.number_input("Ideal Temperature Maximum (°C)", value=40.0, step=0.5)

    # Compute crop outcome for each month.
    climate_df["Crop Outcome"] = climate_df.apply(
        lambda row: compute_crop_outcome(row, ideal_rain_min, ideal_rain_max, ideal_temp_min, ideal_temp_max),
        axis=1
    )
    climate_df["Year"] = climate_df["Period"].dt.year

    # Compute yearly summary.
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

    # Multi-tab layout.
    tabs = st.tabs(["Overview", "Monthly Trends", "Yearly Review", "Forecast", "Download Data"])

    # ---------------------------------------------------------------------
    # Tab 1: Overview – Automated Insights and Data Table
    # ---------------------------------------------------------------------
    with tabs[0]:
        st.header(f"Overview: {selected_region}")
        st.markdown("#### Automated Yearly Insights")
        insights = []
        for year in sorted(yearly_summary["Year"].unique()):
            row = yearly_summary[yearly_summary["Year"] == year].iloc[0]
            insights.append(f"**{year}**: Avg Rainfall = {row['Avg Rainfall (mm)']:.1f} mm, Avg Temp = {row['Avg Temp (°C)']:.1f}°C, Dominant Outcome: **{row['Dominant Outcome']}**.")
        st.markdown("\n\n".join(insights))
        st.markdown("#### Detailed Monthly Climate Data")
        st.dataframe(climate_df[["Period_str", "Rainfall", "Temperature", "Crop Outcome"]])

    # ---------------------------------------------------------------------
    # Tab 2: Monthly Trends – Interactive Line Charts
    # ---------------------------------------------------------------------
    with tabs[1]:
        st.header("Monthly Climate Trends")
        # Rainfall Trend
        fig_rain = px.line(climate_df, x="Period_str", y="Rainfall",
                           title="Monthly Rainfall Trend (mm)", markers=True, template="plotly_white")
        # Temperature Trend
        fig_temp = px.line(climate_df, x="Period_str", y="Temperature",
                           title="Monthly Temperature Trend (°C)", markers=True, template="plotly_white")
        st.plotly_chart(fig_rain, use_container_width=True)
        st.plotly_chart(fig_temp, use_container_width=True)

    # ---------------------------------------------------------------------
    # Tab 3: Yearly Review – Yearly Distribution of Crop Outcomes
    # ---------------------------------------------------------------------
    with tabs[2]:
        st.header("Yearly Crop Outcome Review")
        outcome_year = climate_df.groupby(["Year", "Crop Outcome"]).size().reset_index(name="Count")
        fig_year = px.bar(outcome_year, x="Year", y="Count", color="Crop Outcome",
                          title="Yearly Distribution of Crop Outcomes", barmode="stack", template="plotly_white")
        st.plotly_chart(fig_year, use_container_width=True)
        st.markdown("#### Yearly Climate Summary")
        st.dataframe(yearly_summary)

    # ---------------------------------------------------------------------
    # Tab 4: Forecast – Future Climate Prediction Using Prophet
    # ---------------------------------------------------------------------
    with tabs[3]:
        st.header("Climate Forecasting")
        forecast_metric = st.selectbox("Select Metric to Forecast:", ["Rainfall", "Temperature"])
        st.markdown("Forecasting the next 12 months using Prophet.")
        forecast_df = forecast_climate(climate_df, forecast_metric, periods=12)
        fig_forecast = go.Figure()
        fig_forecast.add_trace(go.Scatter(x=climate_df["Period_str"], y=climate_df[forecast_metric],
                                          mode="markers+lines", name="Historical"))
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

    # ---------------------------------------------------------------------
    # Tab 5: Download Data – Export Climate Data as CSV
    # ---------------------------------------------------------------------
    with tabs[4]:
        st.header("Download Climate Data")
        csv_data = climate_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download as CSV", csv_data, "climate_data.csv", "text/csv")

    st.success("✅ Climate Insights Dashboard loaded successfully!")

# For standalone testing, uncomment below:
# if __name__ == "__main__":
#     yearly_crop_review_dashboard(pd.DataFrame())
