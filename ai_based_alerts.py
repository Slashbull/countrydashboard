# ai_based_alerts.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy import stats

def ai_based_alerts_dashboard(data: pd.DataFrame):
    st.header("🔮 AI-Based Alerts")
    partner_trend = data.groupby(["Partner", "Period"])["Tons"].sum().unstack(fill_value=0)
    if partner_trend.shape[1] < 2:
        st.info("Not enough periods for alerts.")
        return
    pct_change = partner_trend.pct_change(axis=1) * 100
    pct_change = pct_change.round(2)
    latest_period = pct_change.columns[-1]
    threshold = st.slider("Alert Threshold (% Change)", 0, 100, 20, step=5)
    alerts = pct_change[pct_change[latest_period].abs() >= threshold][[latest_period]].reset_index()
    alerts.columns = ["Partner", "Latest % Change"]
    st.markdown("#### Alerts (Partners with significant change)")
    st.dataframe(alerts)
    if not alerts.empty:
        fig = px.bar(alerts, x="Partner", y="Latest % Change",
                     title="Partners Exceeding Threshold", text_auto=True,
                     color="Latest % Change", color_continuous_scale="RdYlGn")
        st.plotly_chart(fig, use_container_width=True)
