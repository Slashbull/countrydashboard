# ai_based_alerts.py
import streamlit as st
import pandas as pd
from data_loader import load_data

def show_ai_based_alerts():
    st.header("AI-Based Alerts")
    df = load_data()
    # Example: flag months where tonnage is 2 standard deviations above average
    mean_tons = df["Tons"].mean()
    std_tons = df["Tons"].std()
    alerts = df[df["Tons"] > mean_tons + 2 * std_tons]
    
    if not alerts.empty:
        st.write("Alerts: Unusually high tonnage detected in the following records:")
        st.dataframe(alerts)
    else:
        st.write("No anomalies detected.")
