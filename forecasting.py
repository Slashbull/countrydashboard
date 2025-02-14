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
    Use the tabs below to view historical data and adjust forecasting parameters, then see the forecast results.
    """)
    
    # Validate required columns.
    required_cols = ["Period", "Tons"]
    missing = [col for col in required_cols if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing required columns: {', '.join(missing)}")
        return

    # Aggregate monthly trade volume.
    monthly = data.groupby("Period", as_index=False)["Tons"].sum()
    monthly = monthly.sort_values("Period")
    
    # Create two tabs: one for settings, one for results.
    tabs = st.tabs(["Historical Data & Settings", "Forecast Results"])
    
    with tabs[0]:
        st.markdown("#### Historical Data")
        st.dataframe(monthly)
        
        # Forecasting method selection.
        method = st.selectbox("Select Forecasting Method", 
                              ["Rolling Average", "Linear Regression", "ARIMA Model"])
        st.session_state["forecast_method"] = method
        
        if method == "Rolling Average":
            st.markdown("##### Rolling Average Settings")
            window = st.slider("Select Rolling Window (number of periods)", 
                               min_value=2, 
                               max_value=min(12, len(monthly)), 
                               value=3)
            st.session_state["rolling_window"] = window
        elif method == "Linear Regression":
            st.markdown("##### Linear Regression Settings")
            st.info("This method uses a simple time index to forecast the next period.")
        elif method == "ARIMA Model":
            st.markdown("##### ARIMA Model Settings")
            p = st.number_input("AR (p)", min_value=0, max_value=5, value=1, step=1)
            d = st.number_input("I (d)", min_value=0, max_value=2, value=1, step=1)
            q = st.number_input("MA (q)", min_value=0, max_value=5, value=1, step=1)
            st.session_state["arima_order"] = (p, d, q)
    
    with tabs[1]:
        st.markdown("#### Forecast Results")
        forecast_value = None
        method = st.session_state.get("forecast_method", "Rolling Average")
        
        if method == "Rolling Average":
            window = st.session_state.get("rolling_window", 3)
            monthly["Forecast"] = monthly["Tons"].rolling(window=window, min_periods=1).mean()
            forecast_value = monthly["Forecast"].iloc[-1]
            st.markdown(f"**Rolling Average Forecast for Next Period: {forecast_value:,.2f} Tons**")
        elif method == "Linear Regression":
            monthly = monthly.copy().reset_index(drop=True)
            monthly["TimeIndex"] = monthly.index
            model = LinearRegression()
            X = monthly[["TimeIndex"]]
            y = monthly["Tons"]
            model.fit(X, y)
            next_index = monthly["TimeIndex"].max() + 1
            forecast_value = model.predict([[next_index]])[0]
            monthly["Forecast"] = model.predict(X)
            st.markdown(f"**Linear Regression Forecast for Next Period: {forecast_value:,.2f} Tons**")
        elif method == "ARIMA Model":
            order = st.session_state.get("arima_order", (1, 1, 1))
            try:
                model = ARIMA(monthly["Tons"], order=order)
                model_fit = model.fit()
                forecast_result = model_fit.forecast(steps=1)
                forecast_value = forecast_result.iloc[0]
                monthly["Forecast"] = model_fit.predict(start=0, end=len(monthly)-1)
                st.markdown(f"**ARIMA Forecast for Next Period: {forecast_value:,.2f} Tons**")
            except Exception as e:
                st.error("Error fitting ARIMA model. Please check parameters and data.")
                st.error(e)
                return

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
        st.success("✅ Forecasting completed successfully!")
