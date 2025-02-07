# time_series_decomposition.py
import streamlit as st
import pandas as pd
import plotly.express as px
from statsmodels.tsa.seasonal import seasonal_decompose

def time_series_decomposition_dashboard(data: pd.DataFrame):
    st.header("📉 Time Series Decomposition")
    if "Period" not in data.columns or "Tons" not in data.columns:
        st.error("Required columns missing.")
        return
    ts = data.groupby("Period")["Tons"].sum().reset_index()
    ts = ts.sort_values("Period")
    try:
        ts.index = pd.to_datetime(ts["Period"], format="%b-%Y")
    except Exception as e:
        st.error("Error converting Period to datetime.")
        return
    result = seasonal_decompose(ts["Tons"], model='additive', period=12)
    st.subheader("Trend")
    st.line_chart(result.trend)
    st.subheader("Seasonality")
    st.line_chart(result.seasonal)
    st.subheader("Residuals")
    st.line_chart(result.resid)
