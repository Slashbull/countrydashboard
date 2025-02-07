# market_overview.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def market_overview_dashboard(data: pd.DataFrame):
    st.header("📊 Market Overview")
    
    # Ensure Period column exists (created during preprocessing)
    if "Period" not in data.columns:
        st.error("Period column missing. Check Month and Year fields.")
        return

    total_volume = data["Tons"].sum()
    unique_partners = data["Partner"].nunique()
    avg_volume = total_volume / unique_partners if unique_partners > 0 else 0

    st.subheader("Key Performance Indicators")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Volume (Tons)", f"{total_volume:,.2f}")
    col2.metric("Unique Partners", unique_partners)
    col3.metric("Avg Volume per Partner", f"{avg_volume:,.2f}")
    
    st.subheader("Monthly Import Trends")
    monthly = data.groupby("Period")["Tons"].sum().reset_index()
    fig = px.line(monthly, x="Period", y="Tons", title="Monthly Volume Trend", markers=True)
    st.plotly_chart(fig, use_container_width=True)
