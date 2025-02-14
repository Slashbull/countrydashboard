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
    Select the forecasting method, adjust parameters, and choose how many future periods to forecast.
    """)

    # Validate required columns.
    required_cols = ["Period", "Tons"]
    missing = [col for col in required_cols if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing required columns: {', '.join(missing)}")
        return

    # Aggregate monthly trade volume.
    monthly = data.groupby("Period", as_index=False)["Tons"].sum().sort_values("Period")
    
    # Forecast horizon selector: number of future periods to forecast.
    forecast_horizon = st.slider("Forecast Horizon (number of periods)", 
                                 min_value=1, max_value=6, value=1)
    
    # Use a two-tab layout: one for settings/historical data and one for forecast results.
    tabs = st.tabs(["Historical Data & Settings", "Forecast Results"])
    
    with tabs[0]:
        st.markdown("#### Historical Data")
        st.dataframe(monthly)
        
        # Forecasting method selection.
        method = st.selectbox("Select Forecasting Method", 
                              ["Rolling Average", "Linear Regression", "ARIMA Model"])
        st.markdown("##### Forecast Settings")
        st.write(f"**Method Selected:** {method}")
        
        # Store parameters based on method.
        if method == "Rolling Average":
            window = st.slider("Rolling Window (periods)", min_value=2, max_value=min(12, len(monthly)), value=3)
        elif method == "ARIMA Model":
            p = st.number_input("AR (p)", min_value=0, max_value=5, value=1, step=1)
            d = st.number_input("I (d)", min_value=0, max_value=2, value=1, step=1)
            q = st.number_input("MA (q)", min_value=0, max_value=5, value=1, step=1)
            arima_order = (p, d, q)
            st.write(f"ARIMA Order: {arima_order}")
        st.info(f"Forecast Horizon: {forecast_horizon} period(s)")
    
    with tabs[1]:
        st.markdown("#### Forecast Results")
        forecast_df = monthly.copy()
        method = st.session_state.get("forecast_method", None)  # Not used here; using local 'method'
        forecast_values = []
        forecast_ci_lower = None
        forecast_ci_upper = None
        
        if method == "Rolling Average" or method is None:
            # For Rolling Average, use the average of the last window and repeat for each future period.
            window = st.session_state.get("rolling_window", 3)
            # Calculate rolling average on historical data.
            forecast_df["Forecast"] = forecast_df["Tons"].rolling(window=window, min_periods=1).mean()
            last_forecast = forecast_df["Forecast"].iloc[-1]
            forecast_values = [last_forecast] * forecast_horizon
            st.markdown(f"**Rolling Average Forecast (constant): {last_forecast:,.2f} Tons per period**")
        elif method == "Linear Regression":
            forecast_df = forecast_df.reset_index(drop=True)
            forecast_df["TimeIndex"] = forecast_df.index
            model = LinearRegression()
            X = forecast_df[["TimeIndex"]]
            y = forecast_df["Tons"]
            model.fit(X, y)
            # Generate predictions for future periods.
            next_indices = np.arange(forecast_df["TimeIndex"].max() + 1, forecast_df["TimeIndex"].max() + forecast_horizon + 1).reshape(-1,1)
            forecast_values = model.predict(next_indices).tolist()
            # For historical forecast, we already predict the training data.
            forecast_df["Forecast"] = model.predict(X)
            st.markdown(f"**Linear Regression Forecast for next {forecast_horizon} period(s):**")
        elif method == "ARIMA Model":
            order = st.session_state.get("arima_order", (1, 1, 1))
            try:
                model = ARIMA(forecast_df["Tons"], order=order)
                model_fit = model.fit()
                forecast_result = model_fit.get_forecast(steps=forecast_horizon)
                forecast_values = forecast_result.predicted_mean.tolist()
                conf_int = forecast_result.conf_int()
                forecast_ci_lower = conf_int.iloc[:, 0].tolist()
                forecast_ci_upper = conf_int.iloc[:, 1].tolist()
                st.markdown(f"**ARIMA Forecast for next {forecast_horizon} period(s):**")
            except Exception as e:
                st.error("Error fitting ARIMA model. Please check parameters and data.")
                st.error(e)
                return

        # Create forecast period labels.
        last_label = forecast_df["Period"].iloc[-1]
        forecast_periods = [f"Next Period {i+1}" for i in range(forecast_horizon)]
        
        # Create a new DataFrame for forecast.
        forecast_future = pd.DataFrame({
            "Period": forecast_periods,
            "Tons": [np.nan] * forecast_horizon,
            "Forecast": forecast_values
        })
        
        # Combine historical and forecast data.
        combined_df = pd.concat([forecast_df, forecast_future], ignore_index=True)
        st.markdown("#### Combined Forecast Data")
        st.dataframe(combined_df)
        
        # Plot actual vs. forecast.
        fig = go.Figure()
        # Actual data trace.
        fig.add_trace(go.Scatter(
            x=combined_df["Period"],
            y=combined_df["Tons"],
            mode="lines+markers",
            name="Actual",
            line=dict(color="blue")
        ))
        # Forecast data trace.
        fig.add_trace(go.Scatter(
            x=combined_df["Period"],
            y=combined_df["Forecast"],
            mode="lines+markers",
            name="Forecast",
            line=dict(dash="dash", color="red")
        ))
        # If ARIMA, add confidence interval as a filled area.
        if method == "ARIMA Model" and forecast_ci_lower is not None and forecast_ci_upper is not None:
            # Create x for forecast periods.
            x_forecast = forecast_periods
            fig.add_trace(go.Scatter(
                x=x_forecast + x_forecast[::-1],
                y=forecast_ci_upper + forecast_ci_lower[::-1],
                fill='toself',
                fillcolor='rgba(255, 0, 0, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip",
                showlegend=True,
                name="Confidence Interval"
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
