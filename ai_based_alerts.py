# ai_based_alerts.py
import streamlit as st
import pandas as pd

def show_ai_based_alerts():
    st.header("AI-Based Alerts")
    from core_system import df  # Use the global data
    # Simple example: Flag records where 'Tons' is 2 standard deviations above mean.
    mean_tons = df["Tons"].mean()
    std_tons = df["Tons"].std()
    alerts = df[df["Tons"] > mean_tons + 2 * std_tons]
    if not alerts.empty:
        st.write("Anomalies detected:")
        st.dataframe(alerts)
    else:
        st.write("No anomalies detected.")
