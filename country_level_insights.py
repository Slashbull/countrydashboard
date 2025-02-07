# country_level_insights.py
import streamlit as st
import pandas as pd
import plotly.express as px

def country_level_insights_dashboard(data: pd.DataFrame):
    st.header("🌍 Country-Level Insights")
    if "Reporter" not in data.columns:
        st.error("Reporter column missing.")
        return
    country_data = data.groupby("Reporter")["Tons"].sum().reset_index()
    fig = px.bar(country_data, x="Reporter", y="Tons", title="Volume by Reporter", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)
