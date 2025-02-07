# market_overview.py
import streamlit as st
import pandas as pd
import altair as alt
from data_loader import load_data
from calculations import calculate_kpis
from filters import add_filters

def show_market_overview():
    st.header("Market Overview")
    # Load data
    df = load_data()
    # Apply filters
    df = add_filters(df)
    # Calculate KPIs
    kpis = calculate_kpis(df)
    col1, col2 = st.columns(2)
    col1.metric("Total Tonnage", f"{kpis['total_tons']:.2f}")
    col2.metric("Average Monthly", f"{kpis['avg_monthly']:.2f}")
    
    # Time series chart
    chart = alt.Chart(df).mark_line(point=True).encode(
        x='Date:T',
        y='sum(Tons):Q',
        tooltip=['Date:T', alt.Tooltip('sum(Tons):Q', title="Tonnage", format=",.2f")]
    ).properties(
        width=700,
        height=400
    ).interactive()
    st.altair_chart(chart, use_container_width=True)
