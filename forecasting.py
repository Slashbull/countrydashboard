# forecasting.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.arima.model import ARIMA

def forecasting_dashboard(data: pd.DataFrame):
    st.title("🔮 Forecasting Dashboard")
    st.markdown("""
    Forecast future trade volume using multiple methods.  
    Choose a method below:
    - **Rolling Average:** Smooths historical data over a window.
    - **Linear Regression:** Fits a trendline to predict the next period.
    - **ARIMA Model:** Uses time series modeling for forecasting.
    """)

    # Validate required columns.
    required_cols = ["Period", "Tons"]
    missing = [col for col in required_cols if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing required columns for forecasting: {', '.join(missing)}")
        return

    # Aggregate monthly trade volume.
    monthly = data.groupby("Period", as_index=False)["Tons"].sum()
    monthly = monthly.sort_values("Period")
    st.markdown("#### Historical Data")
    st.dataframe(monthly)

    if len(monthly) < 3:
        st.info("Not enough data to generate a robust forecast. Need at least 3 periods.")
        return

    # Forecasting method selection.
    method = st.selectbox("Select Forecasting Method", 
                          ["Rolling Average", "Linear Regression", "ARIMA Model"])

    forecast_value = None
    if method == "Rolling Average":
        st.markdown("##### Rolling Average Forecast")
        window = st.slider("Select Rolling Window (number of periods)", 
                           min_value=2, 
                           max_value=min(12, len(monthly)), 
                           value=3)
        monthly["Forecast"] = monthly["Tons"].rolling(window=window, min_periods=1).mean()
        forecast_value = monthly["Forecast"].iloc[-1]

    elif method == "Linear Regression":
        st.markdown("##### Linear Regression Forecast")
        # Reset index to create a time index.
        monthly = monthly.copy().reset_index(drop=True)
        monthly["TimeIndex"] = monthly.index
        model = LinearRegression()
        X = monthly[["TimeIndex"]]
        y = monthly["Tons"]
        model.fit(X, y)
        next_index = monthly["TimeIndex"].max() + 1
        forecast_value = model.predict([[next_index]])[0]
        monthly["Forecast"] = model.predict(X)

    elif method == "ARIMA Model":
        st.markdown("##### ARIMA Forecast")
        st.markdown("Configure ARIMA parameters:")
        p = st.number_input("AR (p)", min_value=0, max_value=5, value=1, step=1)
        d = st.number_input("I (d)", min_value=0, max_value=2, value=1, step=1)
        q = st.number_input("MA (q)", min_value=0, max_value=5, value=1, step=1)
        try:
            # Fit ARIMA model on the historical Tons data.
            model = ARIMA(monthly["Tons"], order=(p, d, q))
            model_fit = model.fit()
            forecast_result = model_fit.forecast(steps=1)
            forecast_value = forecast_result.iloc[0]
            monthly["Forecast"] = model_fit.predict(start=0, end=len(monthly)-1)
        except Exception as e:
            st.error("Error fitting ARIMA model. Please check your parameters and data.")
            st.error(e)
            return

    st.markdown(f"**Forecast for Next Period ({method}): {forecast_value:,.2f} Tons**")

    # Append forecast row.
    forecast_row = pd.DataFrame({
        "Period": ["Next Period"],
        "Tons": [np.nan],
        "Forecast": [forecast_value]
    })
    forecast_data = pd.concat([monthly, forecast_row], ignore_index=True)

    st.markdown("#### Forecast Data")
    st.dataframe(forecast_data)

    # Plot actual vs. forecast.
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=forecast_data["Period"],
        y=forecast_data["Tons"],
        mode="lines+markers",
        name="Actual",
        line=dict(color="blue")
    ))
    fig.add_trace(go.Scatter(
        x=forecast_data["Period"],
        y=forecast_data["Forecast"],
        mode="lines+markers",
        name="Forecast",
        line=dict(dash="dash", color="red")
    ))
    fig.update_layout(
        title="Actual vs Forecast Trade Volume",
        xaxis_title="Period",
        yaxis_title="Volume (Tons)",
        template="plotly_white",
        margin=dict(l=40, r=40, t=40, b=40)
    )
    st.plotly_chart(fig, use_container_width=True)
    st.success("✅ Forecasting Dashboard loaded successfully!")
