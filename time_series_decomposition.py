# time_series_decomposition.py
import streamlit as st
import pandas as pd
import plotly.express as px
from statsmodels.tsa.seasonal import seasonal_decompose

def time_series_decomposition_dashboard(data: pd.DataFrame):
    st.title("📉 Time Series Decomposition Dashboard")
    st.markdown("""
    Decompose your trade volume time series into trend, seasonal, and residual components.
    
    **Instructions:**
    - Ensure your data has a 'Period' column in the format like "Jan-2012".
    - The 'Tons' column will be aggregated by Period.
    - Choose the decomposition model (additive or multiplicative) and set the seasonal period.
    """)

    # Validate required columns.
    required_cols = ["Period", "Tons"]
    missing = [col for col in required_cols if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing required columns: {', '.join(missing)}")
        return

    # Convert Tons to numeric.
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")

    # Aggregate data by Period.
    ts_data = data.groupby("Period", as_index=False)["Tons"].sum()
    ts_data = ts_data.sort_values("Period")

    # Convert Period to datetime.
    try:
        ts_data["Period_dt"] = pd.to_datetime(ts_data["Period"], format="%b-%Y")
    except Exception as e:
        st.error("Error converting 'Period' to datetime. Ensure it is in the format 'Jan-2012'.")
        st.error(e)
        return

    ts_data = ts_data.set_index("Period_dt")
    
    st.markdown("#### Historical Trade Volume")
    st.line_chart(ts_data["Tons"])

    st.markdown("### Decomposition Settings")
    model_type = st.selectbox("Select Decomposition Model", ["additive", "multiplicative"])
    period_value = st.number_input("Seasonal Period (number of observations per cycle)", min_value=2, max_value=36, value=12, step=1)

    # Perform time series decomposition.
    try:
        result = seasonal_decompose(ts_data["Tons"], model=model_type, period=period_value)
    except Exception as e:
        st.error("Error during time series decomposition. Your data might not have enough observations for the selected period.")
        st.error(e)
        return

    # Plot Trend Component.
    st.subheader("Trend Component")
    fig_trend = px.line(result.trend.reset_index(), x="Period_dt", y="Tons", title="Trend Component")
    fig_trend.update_layout(xaxis_title="Period", yaxis_title="Volume (Tons)")
    st.plotly_chart(fig_trend, use_container_width=True)

    # Plot Seasonal Component.
    st.subheader("Seasonal Component")
    fig_seasonal = px.line(result.seasonal.reset_index(), x="Period_dt", y="Tons", title="Seasonal Component")
    fig_seasonal.update_layout(xaxis_title="Period", yaxis_title="Volume (Tons)")
    st.plotly_chart(fig_seasonal, use_container_width=True)

    # Plot Residual Component.
    st.subheader("Residual Component")
    fig_resid = px.line(result.resid.reset_index(), x="Period_dt", y="Tons", title="Residual Component")
    fig_resid.update_layout(xaxis_title="Period", yaxis_title="Volume (Tons)")
    st.plotly_chart(fig_resid, use_container_width=True)

    st.success("✅ Time Series Decomposition completed successfully!")
