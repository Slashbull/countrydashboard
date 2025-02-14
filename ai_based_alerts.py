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
    
    # Get the label for the latest period
    latest_period = pct_change.columns[-1]
    st.info(f"Calculations are based on the latest period: {latest_period}")

    # Let user choose the alert method.
    alert_method = st.radio("Select Alert Method:", 
                            ["Basic Threshold", "Advanced Anomaly Detection", "Comparison"])

    # ----- Basic Threshold Mode -----
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
            # Download button for alerts table.
            st.download_button("Download Alerts as CSV", basic_alerts.to_csv(index=False).encode("utf-8"), "basic_alerts.csv", "text/csv")
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

    # ----- Advanced Anomaly Detection Mode -----
    elif alert_method == "Advanced Anomaly Detection":
        st.subheader("Advanced Anomaly Detection Alerts")
        st.markdown("Using IsolationForest to detect anomalies in the latest period's percentage changes.")
        contamination = st.slider("IsolationForest Contamination (Expected Outlier Fraction)",
                                  min_value=0.01, max_value=0.5, value=0.1, step=0.01)
        # Prepare data: latest period percentage changes.
        latest_pct = pct_change[latest_period].fillna(0).values.reshape(-1, 1)
        model = IsolationForest(contamination=contamination, random_state=42)
        preds = model.fit_predict(latest_pct)
        anomalies = pct_change[latest_period][preds == -1]
        anomalies_df = anomalies.reset_index().rename(columns={latest_period: "Latest % Change"})
        anomalies_df.columns = ["Partner", "Latest % Change"]
        st.markdown("**Anomaly Alerts (Advanced):**")
        if anomalies_df.empty:
            st.success("✅ No anomalies detected.")
        else:
            st.dataframe(anomalies_df)
            st.download_button("Download Anomaly Alerts as CSV", anomalies_df.to_csv(index=False).encode("utf-8"), "advanced_alerts.csv", "text/csv")
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

    # ----- Comparison Mode -----
    elif alert_method == "Comparison":
        st.subheader("Comparison of Basic and Advanced Methods")
        # Basic method parameters.
        basic_threshold = st.slider("Basic Method Alert Threshold (% Change)", min_value=0, max_value=100, value=20, step=5, key="comp_threshold")
        basic_alerts = pct_change[pct_change[latest_period].abs() >= basic_threshold][[latest_period]].reset_index()
        basic_alerts.columns = ["Partner", "Latest % Change"]

        # Advanced method parameters.
        adv_contamination = st.slider("Advanced Method Contamination", min_value=0.01, max_value=0.5, value=0.1, step=0.01, key="comp_contam")
        latest_pct = pct_change[latest_period].fillna(0).values.reshape(-1, 1)
        model = IsolationForest(contamination=adv_contamination, random_state=42)
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
                st.download_button("Download Basic Alerts as CSV", basic_alerts.to_csv(index=False).encode("utf-8"), "basic_alerts.csv", "text/csv")
        with col2:
            st.markdown("**Advanced Anomaly Alerts:**")
            if advanced_alerts.empty:
                st.success("✅ No advanced anomalies detected.")
            else:
                st.dataframe(advanced_alerts)
                st.download_button("Download Advanced Alerts as CSV", advanced_alerts.to_csv(index=False).encode("utf-8"), "advanced_alerts.csv", "text/csv")
        
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
