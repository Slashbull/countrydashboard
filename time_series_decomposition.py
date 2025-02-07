# time_series_decomposition.py
import streamlit as st
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose

def show_time_series_decomposition():
    st.header("Time Series Decomposition")
    from core_system import data  # Global data
    from filters import add_filters
    df_filtered = add_filters(data)
    df_sorted = df_filtered.sort_values("Date")
    ts = df_sorted.groupby("Date")["Tons"].sum()
    try:
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
    except Exception as e:
        st.error(f"Error in decomposition: {e}")
