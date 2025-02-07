# forecasting.py
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

def forecasting_dashboard(data: pd.DataFrame):
    st.header("🔮 Forecasting")
    monthly = data.groupby("Period")["Tons"].sum().reset_index()
    monthly = monthly.sort_values("Period")
    st.markdown("#### Historical Data")
    st.dataframe(monthly)
    if len(monthly) < 3:
        st.info("Not enough data to forecast.")
        return
    monthly["Forecast"] = monthly["Tons"].rolling(window=3).mean()
    forecast_value = monthly["Forecast"].iloc[-1]
    forecast_df = pd.DataFrame({"Period": ["Next Period"], "Tons": [np.nan], "Forecast": [forecast_value]})
    forecast_data = pd.concat([monthly, forecast_df], ignore_index=True)
    st.markdown("#### Forecast Data")
    st.dataframe(forecast_data)
    fig = px.line(forecast_data, x="Period", y="Tons", title="Actual vs Forecast", markers=True)
    fig.add_scatter(x=forecast_data["Period"], y=forecast_data["Forecast"],
                    mode="lines+markers", name="Forecast",
                    line=dict(dash="dash", color="red"))
    st.plotly_chart(fig, use_container_width=True)
