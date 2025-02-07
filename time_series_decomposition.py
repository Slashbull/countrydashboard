# time_series_decomposition.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from data_loader import load_data
from filters import add_filters

def show_time_series_decomposition():
    st.header("Time Series Decomposition")
    df = load_data()
    df = add_filters(df)
    
    # Ensure data is sorted by date
    df = df.sort_values("Date")
    ts = df.groupby("Date")["Tons"].sum()
    
    # Decompose the time series
    result = seasonal_decompose(ts, model='additive', period=12)
    
    fig, axes = plt.subplots(4, 1, figsize=(10, 8), sharex=True)
    result.observed.plot(ax=axes[0], legend=False)
    axes[0].set_ylabel("Observed")
    result.trend.plot(ax=axes[1], legend=False)
    axes[1].set_ylabel("Trend")
    result.seasonal.plot(ax=axes[2], legend=False)
    axes[2].set_ylabel("Seasonal")
    result.resid.plot(ax=axes[3], legend=False)
    axes[3].set_ylabel("Residual")
    
    st.pyplot(fig)
