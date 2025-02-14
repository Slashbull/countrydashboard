# climate_insights.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from prophet import Prophet
from datetime import datetime

# -----------------------------------
# Helper: Simulate Historical Climate Data
# -----------------------------------
def simulate_historical_climate(start_year=2012, end_year=None, country="IRAQ"):
    """
    Simulate monthly average climate data (avg daily precipitation in mm/day and avg maximum temperature in °C)
    from start_year to the current year for a given country.
    
    These base values are approximate for key date-growing regions.
    """
    if end_year is None:
        end_year = datetime.now().year
    dates = pd.date_range(start=f"{start_year}-01-01", end=f"{end_year}-12-31", freq="M")
    
    # Base values per country (example approximations)
    base_precip = {
        "IRAQ": 0.6,
        "UNITED ARAB EMIRATES": 0.55,
        "IRAN": 0.65,
        "SAUDI ARABIA": 0.50,
        "TUNISIA": 0.70,
        "ALGERIA": 0.75,
        "ISRAEL": 0.60,
        "JORDAN": 0.65,
        "STATE OF PALESTINE": 0.70
    }
    base_temp = {
        "IRAQ": 42,
        "UNITED ARAB EMIRATES": 43,
        "IRAN": 41,
        "SAUDI ARABIA": 44,
        "TUNISIA": 39,
        "ALGERIA": 40,
        "ISRAEL": 38,
        "JORDAN": 40,
        "STATE OF PALESTINE": 39
    }
    base_p = base_precip.get(country.upper(), 0.65)
    base_t = base_temp.get(country.upper(), 42)
    
    # Simulate some seasonal variation: use a sine wave to mimic seasonal patterns.
    months = np.array([d.month for d in dates])
    seasonal_factor = np.sin(2 * np.pi * (months-1)/12)
    
    # Generate precipitation: add random noise.
    precip = [max(0, base_p + 0.1 * seasonal_factor[i] + np.random.normal(0, 0.05))
              for i in range(len(dates))]
    # Generate temperature: assume higher in summer, lower in winter.
    temp = [base_t + 2 * seasonal_factor[i] + np.random.normal(0, 1)
            for i in range(len(dates))]
    
    df = pd.DataFrame({
        "Date": dates,
        "Avg Precipitation (mm/day)": precip,
        "Avg Max Temperature (°C)": temp
    })
    return df

# -----------------------------------
# Helper: Assess Date Crop Quality Based on Climate
# -----------------------------------
def assess_crop_quality(avg_precip, avg_max_temp):
    """
    Compute crop quality score based on average daily precipitation and average max temperature.
    Ideal conditions for date palms are:
      - Low precipitation: less than ~0.5 mm/day is ideal.
      - High maximum temperature in an optimal range (e.g., 38-42°C).
      
    Precipitation Score:
      - < 0.5 mm/day: 5
      - 0.5-0.7: 4
      - 0.7-0.9: 3
      - 0.9-1.1: 2
      - >= 1.1: 1
      
    Temperature Score:
      - 38-42°C: 5
      - 36-38 or 42-44°C: 4
      - 34-36 or 44-46°C: 3
      - 32-34 or 46-48°C: 2
      - Otherwise: 1
      
    Overall Score = 0.6 * (Precipitation Score) + 0.4 * (Temperature Score)
    Final Rating:
      - >= 4.5: EXCELLENT
      - >= 4: VERY GOOD
      - >= 3: GOOD
      - >= 2: MODERATE
      - Else: BAD
    """
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

    # Temperature score
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
    return rating, overall_score

# -----------------------------------
# Helper: Forecast Future Climate Trend using Prophet (on precipitation)
# -----------------------------------
def forecast_climate(hist_df, periods=12):
    """
    Use Prophet to forecast monthly average precipitation.
    """
    from prophet import Prophet
    df_prophet = hist_df.rename(columns={"Date": "ds", "Avg Precipitation (mm/day)": "y"})
    model = Prophet(yearly_seasonality=True, daily_seasonality=False)
    model.fit(df_prophet)
    future = model.make_future_dataframe(periods=periods, freq="M")
    forecast = model.predict(future)
    return forecast, model

# -----------------------------------
# Main Dashboard Function
# -----------------------------------
def climate_insights_dashboard():
    st.title("🌦 Historical & Forecast Climate Insights for Date Crop Analysis")
    st.markdown("""
    This dashboard simulates historical monthly climate data (2012–present) for key date‑growing regions and uses it to:
    - Visualize historical trends in precipitation and temperature.
    - Forecast future precipitation trends.
    - Assess the expected quality of the date crop based on climate conditions.
    
    **Key Factors:**
    - Date palms thrive in hot, arid climates with very low rainfall.
    - Excessive rainfall or suboptimal temperatures can harm crop quality.
    """)

    # Let the user select a partner country (date-growing region)
    partner_options = ["IRAQ", "UNITED ARAB EMIRATES", "IRAN", "SAUDI ARABIA", "TUNISIA", "ALGERIA", "ISRAEL", "JORDAN", "STATE OF PALESTINE"]
    selected_country = st.selectbox("Select a Date-Growing Country:", partner_options)

    # Simulate historical climate data from 2012 to current year.
    hist_df = simulate_historical_climate(start_year=2012, country=selected_country)
    st.markdown("### Historical Monthly Climate Data (Simulated)")
    st.dataframe(hist_df)

    # Display historical trends.
    fig_precip = px.line(
        hist_df,
        x="Date",
        y="Avg Precipitation (mm/day)",
        title=f"Historical Monthly Average Precipitation for {selected_country}",
        markers=True,
        template="plotly_white"
    )
    fig_precip.update_layout(xaxis_title="Date", yaxis_title="Avg Precipitation (mm/day)")
    st.plotly_chart(fig_precip, use_container_width=True)

    fig_temp = px.line(
        hist_df,
        x="Date",
        y="Avg Max Temperature (°C)",
        title=f"Historical Monthly Average Max Temperature for {selected_country}",
        markers=True,
        template="plotly_white"
    )
    fig_temp.update_layout(xaxis_title="Date", yaxis_title="Avg Max Temperature (°C)")
    st.plotly_chart(fig_temp, use_container_width=True)

    # Compute overall historical averages.
    overall_avg_precip = hist_df["Avg Precipitation (mm/day)"].mean()
    overall_avg_temp = hist_df["Avg Max Temperature (°C)"].mean()

    st.markdown(f"**Overall Historical Average Daily Precipitation:** {overall_avg_precip:.2f} mm/day")
    st.markdown(f"**Overall Historical Average Max Temperature:** {overall_avg_temp:.2f} °C")

    # Assess historical crop quality.
    historical_quality, historical_score = assess_crop_quality(overall_avg_precip, overall_avg_temp)
    st.markdown(f"**Historical Crop Quality Rating:** {historical_quality} (Score: {historical_score:.2f})")

    # Forecast future precipitation trends.
    st.markdown("---")
    st.header("Forecast Future Climate Trend (Precipitation)")
    forecast_df, model = forecast_climate(hist_df, periods=12)
    forecast_future = forecast_df[forecast_df["ds"] > hist_df["Date"].max()]
    st.markdown("#### Forecasted Average Daily Precipitation for Next 12 Months")
    st.dataframe(forecast_future[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(12))
    st.markdown("#### Forecast Plot")
    fig_forecast = model.plot(forecast_df)
    st.pyplot(fig_forecast)

    # Use the forecasted average precipitation to predict crop quality.
    # Here we use the forecasted precipitation for the next month as a proxy.
    if not forecast_future.empty:
        forecast_avg_precip = forecast_future["yhat"].iloc[0]
    else:
        forecast_avg_precip = overall_avg_precip

    # For temperature forecasting, we might assume similar temperature patterns as historical average.
    forecast_avg_temp = overall_avg_temp

    predicted_quality, predicted_score = assess_crop_quality(forecast_avg_precip, forecast_avg_temp)
    st.markdown("---")
    st.header("Crop Quality Forecast")
    st.markdown(f"**Forecasted Average Daily Precipitation (Next Month):** {forecast_avg_precip:.2f} mm/day")
    st.markdown(f"**Assumed Average Max Temperature:** {forecast_avg_temp:.2f} °C")
    st.markdown(f"**Predicted Date Crop Quality for Next Month:** {predicted_quality} (Score: {predicted_score:.2f})")

    # Alert if predicted quality is below a user-defined threshold.
    quality_levels = {"EXCELLENT": 5, "VERY GOOD": 4, "GOOD": 3, "MODERATE": 2, "BAD": 1}
    default_threshold = 3  # e.g., GOOD or above is acceptable.
    threshold_level = st.slider("Set Minimum Acceptable Crop Quality Level (1=BAD, 5=EXCELLENT)", min_value=1, max_value=5, value=default_threshold, step=1)
    predicted_level = quality_levels.get(predicted_quality, 3)
    if predicted_level < threshold_level:
        st.error("🚨 Alert: Forecasted crop quality is below the acceptable threshold! Consider reviewing irrigation, climate mitigation strategies, or crop management practices.")
    else:
        st.success("✅ Forecasted crop quality meets the acceptable threshold.")

    st.success("✅ Date Crop Analysis Dashboard loaded successfully!")

if __name__ == "__main__":
    climate_insights_dashboard()
