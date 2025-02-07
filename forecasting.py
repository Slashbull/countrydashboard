# forecasting.py
import streamlit as st
import pandas as pd
import altair as alt
from data_loader import load_data
import numpy as np

def show_forecasting():
    st.header("Forecasting")
    df = load_data()
    # Assume df has a 'Date' and 'Tons' column. We’ll create a simple forecast using a rolling average.
    df = df.sort_values("Date")
    df['Forecast'] = df['Tons'].rolling(window=3, min_periods=1).mean()
    
    line_chart = alt.Chart(df).mark_line(point=True).encode(
        x='Date:T',
        y=alt.Y('Tons:Q', title="Actual Tonnage"),
        tooltip=['Date:T', alt.Tooltip('Tons:Q', format=",.2f")]
    ).properties(width=700, height=400)
    
    forecast_chart = alt.Chart(df).mark_line(color='red').encode(
        x='Date:T',
        y=alt.Y('Forecast:Q', title="Forecast Tonnage"),
        tooltip=[alt.Tooltip('Forecast:Q', format=",.2f")]
    )
    
    st.altair_chart(line_chart + forecast_chart, use_container_width=True)
