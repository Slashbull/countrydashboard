# ai_based_alerts.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import IsolationForest

def ai_based_alerts_dashboard(data: pd.DataFrame):
    st.title("🔮 Advanced AI-Based Alerts")
    st.markdown("""
    This module offers a powerful alerting system for your trade data.  
    Choose between a **Basic Threshold** method and **Advanced Anomaly Detection** using IsolationForest.  
    You can also compare both methods side-by-side.
    """)

    # Validate required columns.
    required_cols = ["Partner", "Period", "Tons"]
    missing = [col for col in required_cols if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing required columns: {', '.join(missing)}")
        return

    # Aggregate data by Partner and Period (summing Tons)
    grouped = data.groupby(["Partner", "Period"])["Tons"].sum().unstack(fill_value=0)
    if grouped.shape[1] < 2:
        st.info("Not enough period data to compute alerts.")
        return

    # Calculate period-over-period percentage change
    pct_change = grouped.pct_change(axis=1) * 100
    pct_change = pct_change.round(2)
    
    # Latest period label
    latest_period = pct_change.columns[-1]

    # Let user choose the alert method.
    alert_method = st.radio("Select Alert Method:", ["Basic Threshold", "Advanced Anomaly Detection", "Comparison"])

    if alert_method == "Basic Threshold":
        st.subheader("Basic Threshold Alerts")
        threshold = st.slider("Alert Threshold (% Change)", min_value=0, max_value=100, value=20, step=5)
        basic_alerts = pct_change[pct_change[latest_period].abs() >= threshold][[latest_period]].reset_index()
        basic_alerts.columns = ["Partner", "Latest % Change"]
        st.markdown("**Alerts (Basic Threshold):**")
        if basic_alerts.empty:
            st.success("✅ No partners exceed the specified threshold.")
        else:
            st.dataframe(basic_alerts)
            fig_basic = px.bar(
                basic_alerts,
                x="Partner",
                y="Latest % Change",
                title="Partners Exceeding Threshold",
                text_auto=True,
                template="plotly_white",
                color="Latest % Change",
                color_continuous_scale="RdYlGn"
            )
            st.plotly_chart(fig_basic, use_container_width=True)

    elif alert_method == "Advanced Anomaly Detection":
        st.subheader("Advanced Anomaly Detection Alerts")
        st.markdown("Using IsolationForest to detect anomalies in the latest period's percentage changes.")
        contamination = st.slider("IsolationForest Contamination (Expected Outlier Fraction)",
                                  min_value=0.01, max_value=0.5, value=0.1, step=0.01)
        # Prepare data: latest period percentage changes.
        latest_pct = pct_change[latest_period].fillna(0).values.reshape(-1, 1)
        model = IsolationForest(contamination=contamination, random_state=42)
        preds = model.fit_predict(latest_pct)
        # Anomalies where prediction == -1.
        anomalies = pct_change[latest_period][preds == -1]
        anomalies_df = anomalies.reset_index().rename(columns={latest_period: "Latest % Change"})
        anomalies_df.columns = ["Partner", "Latest % Change"]
        st.markdown("**Anomaly Alerts (Advanced):**")
        if anomalies_df.empty:
            st.success("✅ No anomalies detected.")
        else:
            st.dataframe(anomalies_df)
            fig_advanced = px.bar(
                anomalies_df,
                x="Partner",
                y="Latest % Change",
                title="Anomaly Alerts by IsolationForest",
                text_auto=True,
                template="plotly_white",
                color="Latest % Change",
                color_continuous_scale="RdYlGn"
            )
            st.plotly_chart(fig_advanced, use_container_width=True)

    elif alert_method == "Comparison":
        st.subheader("Comparison of Basic and Advanced Methods")
        # Basic method parameters.
        threshold = st.slider("Alert Threshold (% Change) for Basic Method", min_value=0, max_value=100, value=20, step=5, key="comp_threshold")
        basic_alerts = pct_change[pct_change[latest_period].abs() >= threshold][[latest_period]].reset_index()
        basic_alerts.columns = ["Partner", "Latest % Change"]

        # Advanced method parameters.
        contamination = st.slider("IsolationForest Contamination (Advanced Method)", min_value=0.01, max_value=0.5, value=0.1, step=0.01, key="comp_contam")
        latest_pct = pct_change[latest_period].fillna(0).values.reshape(-1, 1)
        model = IsolationForest(contamination=contamination, random_state=42)
        preds = model.fit_predict(latest_pct)
        advanced_alerts = pct_change[latest_period][preds == -1].reset_index().rename(columns={latest_period: "Latest % Change"})
        advanced_alerts.columns = ["Partner", "Latest % Change"]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Basic Threshold Alerts:**")
            if basic_alerts.empty:
                st.success("✅ No basic alerts.")
            else:
                st.dataframe(basic_alerts)
        with col2:
            st.markdown("**Advanced Anomaly Alerts:**")
            if advanced_alerts.empty:
                st.success("✅ No advanced anomalies detected.")
            else:
                st.dataframe(advanced_alerts)
        
        st.markdown("---")
        st.markdown("**Combined Bar Chart Comparison:**")
        combined = pd.merge(basic_alerts, advanced_alerts, on="Partner", how="outer", suffixes=("_Basic", "_Advanced"))
        combined.fillna(0, inplace=True)
        if not combined.empty:
            fig_combined = px.bar(
                combined,
                x="Partner",
                y=["Latest % Change_Basic", "Latest % Change_Advanced"],
                title="Comparison of Alert Methods",
                barmode="group",
                template="plotly_white"
            )
            st.plotly_chart(fig_combined, use_container_width=True)
        else:
            st.info("No alerts detected by either method.")

    st.success("✅ Advanced AI-Based Alerts loaded successfully!")
