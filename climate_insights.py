# yearly_crop_review.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# ---------------------------
# Helper: Simulate Historical Climate Data
# ---------------------------
def simulate_historical_climate(start_year=2012, end_year=None, country="IRAQ"):
    """
    Simulate monthly average climate data (average daily precipitation in mm/day and average maximum temperature in °C)
    from start_year to the current year for a given country.
    """
    if end_year is None:
        end_year = datetime.now().year
    dates = pd.date_range(start=f"{start_year}-01-01", end=f"{end_year}-12-31", freq="M")
    
    # Base values per country (example approximations for key date-growing regions)
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
    
    # Use a sine wave to mimic seasonal variation.
    months = np.array([d.month for d in dates])
    seasonal_factor = np.sin(2 * np.pi * (months-1)/12)
    
    # Generate precipitation: add seasonal variation and random noise.
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

# ---------------------------
# Helper: Assess Crop Quality Based on Climate
# ---------------------------
def assess_crop_quality(avg_precip, avg_max_temp):
    """
    Assess date crop quality based on average daily precipitation and average max temperature.
    
    Precipitation thresholds (mm/day):
      - < 0.5  -> Score 5 (EXCELLENT)
      - 0.5 - 0.7 -> Score 4 (VERY GOOD)
      - 0.7 - 0.9 -> Score 3 (GOOD)
      - 0.9 - 1.1 -> Score 2 (MODERATE)
      - >= 1.1  -> Score 1 (BAD)
      
    Temperature thresholds (°C) – ideal range is around 38-42°C:
      - 38-42: Score 5 (EXCELLENT)
      - 36-38 or 42-44: Score 4 (VERY GOOD)
      - 34-36 or 44-46: Score 3 (GOOD)
      - 32-34 or 46-48: Score 2 (MODERATE)
      - Otherwise: Score 1 (BAD)
      
    Overall Score = 0.6 * (Precipitation Score) + 0.4 * (Temperature Score)
    
    Final Rating:
      - Overall Score >= 4.5: EXCELLENT
      - Overall Score >= 4: VERY GOOD
      - Overall Score >= 3: GOOD
      - Overall Score >= 2: MODERATE
      - Otherwise: BAD
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

# ---------------------------
# Main Dashboard Function: Yearly Crop Review
# ---------------------------
def yearly_crop_review_dashboard():
    st.title("📅 Yearly Date Crop Review Dashboard")
    st.markdown("""
    This dashboard reviews historical date crop quality year‑by‑year based on simulated monthly climate data.
    
    **How It Works:**
    - We simulate monthly average climate data (average daily precipitation and maximum temperature) from 2012 to the current year.
    - For each year, we compute the average precipitation and average maximum temperature.
    - These averages are then used to assess the crop quality using a custom scoring function.
    - The results are displayed in a table and a bar chart.
    """)

    # Let the user select a date-growing country.
    partner_options = ["IRAQ", "UNITED ARAB EMIRATES", "IRAN", "SAUDI ARABIA", "TUNISIA", "ALGERIA", "ISRAEL", "JORDAN", "STATE OF PALESTINE"]
    selected_country = st.selectbox("Select a Date-Growing Country:", partner_options)

    # Simulate historical climate data.
    hist_df = simulate_historical_climate(start_year=2012, country=selected_country)
    st.markdown("### Historical Monthly Climate Data (Simulated)")
    st.dataframe(hist_df)

    # Extract Year from Date.
    hist_df["Year"] = hist_df["Date"].dt.year

    # Group by Year: compute average precipitation and temperature per year.
    yearly_summary = hist_df.groupby("Year").agg({
        "Avg Precipitation (mm/day)": "mean",
        "Avg Max Temperature (°C)": "mean"
    }).reset_index()

    # For each year, assess crop quality.
    quality_ratings = []
    quality_scores = []
    for _, row in yearly_summary.iterrows():
        rating, score = assess_crop_quality(row["Avg Precipitation (mm/day)"], row["Avg Max Temperature (°C)"])
        quality_ratings.append(rating)
        quality_scores.append(score)
    yearly_summary["Crop Quality"] = quality_ratings
    yearly_summary["Quality Score"] = quality_scores

    st.markdown("### Yearly Crop Quality Review")
    st.dataframe(yearly_summary)

    # Create a bar chart to visualize the quality score over the years.
    fig = px.bar(
        yearly_summary,
        x="Year",
        y="Quality Score",
        color="Crop Quality",
        title="Yearly Date Crop Quality Score",
        text="Crop Quality",
        template="plotly_white"
    )
    fig.update_layout(xaxis_title="Year", yaxis_title="Quality Score (Higher is Better)")
    st.plotly_chart(fig, use_container_width=True)

    st.success("✅ Yearly Date Crop Review loaded successfully!")

if __name__ == "__main__":
    yearly_crop_review_dashboard()
