# ai_based_alerts.py
import streamlit as st

def show_ai_based_alerts():
    st.header("AI-Based Alerts")
    from core_system import data  # Global data
    mean_val = data["Tons"].mean()
    std_val = data["Tons"].std()
    alerts = data[data["Tons"] > mean_val + 2 * std_val]
    if not alerts.empty:
        st.write("Anomalies detected:")
        st.dataframe(alerts)
    else:
        st.write("No anomalies detected.")
