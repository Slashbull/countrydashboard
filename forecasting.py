# forecasting.py
import streamlit as st
import altair as alt
import pandas as pd

def show_forecasting():
    st.header("Forecasting")
    from core_system import df  # Use global data
    # Sort and compute a simple rolling average forecast (window=3 months)
    df_sorted = df.sort_values("Date")
    df_sorted["Forecast"] = df_sorted["Tons"].rolling(window=3, min_periods=1).mean()
    
    actual_chart = alt.Chart(df_sorted).mark_line(point=True).encode(
        x='Date:T',
        y=alt.Y('Tons:Q', title="Actual Tonnage"),
        tooltip=['Date:T', alt.Tooltip('Tons:Q', format=",.2f")]
    )
    forecast_chart = alt.Chart(df_sorted).mark_line(color='red').encode(
        x='Date:T',
        y=alt.Y('Forecast:Q', title="Forecast Tonnage"),
        tooltip=[alt.Tooltip('Forecast:Q', format=",.2f")]
    )
    st.altair_chart(actual_chart + forecast_chart, use_container_width=True)
