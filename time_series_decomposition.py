# time_series_decomposition.py
import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from statsmodels.tsa.seasonal import seasonal_decompose

def time_series_decomposition_dashboard(data: pd.DataFrame):
    st.title("📉 Time Series Decomposition Dashboard")
    st.markdown("""
    This module decomposes your trade volume time series into trend, seasonal, and residual components.
    
    **Instructions:**
    - Ensure your data has a 'Period' column in the format like "Jan-2012".
    - The 'Tons' column will be aggregated by Period.
    - Choose the decomposition model (additive or multiplicative) and set the seasonal period (e.g., 12 for monthly data with a yearly cycle).
    - You can view the components separately or as a combined plot.
    """)

    # Validate required columns.
    required_cols = ["Period", "Tons"]
    missing = [col for col in required_cols if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing required columns: {', '.join(missing)}")
        return

    # Convert 'Tons' to numeric.
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
    period_value = st.number_input("Seasonal Period (observations per cycle)", min_value=2, max_value=36, value=12, step=1)

    # Choose view mode: individual or combined
    view_mode = st.radio("View Mode", options=["Individual Components", "Combined Plot"])

    # Perform time series decomposition.
    try:
        result = seasonal_decompose(ts_data["Tons"], model=model_type, period=period_value)
    except Exception as e:
        st.error("Error during time series decomposition. Your data might not have enough observations for the selected period.")
        st.error(e)
        return

    if view_mode == "Individual Components":
        # --- Trend Component ---
        st.subheader("Trend Component")
        trend_df = result.trend.reset_index().rename(columns={"index": "Period_dt"})
        if "Tons" not in trend_df.columns:
            trend_df = trend_df.rename(columns={trend_df.columns[1]: "Tons"})
        fig_trend = px.line(trend_df, x="Period_dt", y="Tons", title="Trend Component", template="plotly_white")
        fig_trend.update_layout(xaxis_title="Period", yaxis_title="Volume (Tons)")
        st.plotly_chart(fig_trend, use_container_width=True)

        # --- Seasonal Component ---
        st.subheader("Seasonal Component")
        seasonal_df = result.seasonal.reset_index().rename(columns={"index": "Period_dt"})
        if "Tons" not in seasonal_df.columns:
            seasonal_df = seasonal_df.rename(columns={seasonal_df.columns[1]: "Tons"})
        fig_seasonal = px.line(seasonal_df, x="Period_dt", y="Tons", title="Seasonal Component", template="plotly_white")
        fig_seasonal.update_layout(xaxis_title="Period", yaxis_title="Volume (Tons)")
        st.plotly_chart(fig_seasonal, use_container_width=True)

        # --- Residual Component ---
        st.subheader("Residual Component")
        resid_df = result.resid.reset_index().rename(columns={"index": "Period_dt"})
        if "Tons" not in resid_df.columns:
            resid_df = resid_df.rename(columns={resid_df.columns[1]: "Tons"})
        fig_resid = px.line(resid_df, x="Period_dt", y="Tons", title="Residual Component", template="plotly_white")
        fig_resid.update_layout(xaxis_title="Period", yaxis_title="Volume (Tons)")
        st.plotly_chart(fig_resid, use_container_width=True)
    else:
        # Combined Plot using subplots
        st.subheader("Combined Decomposition Plot")
        fig_combined = make_subplots(rows=4, cols=1, shared_xaxes=True,
                                     subplot_titles=("Original Data", "Trend", "Seasonal", "Residual"))
        # Original series
        fig_combined.add_trace(go.Scatter(x=ts_data.index, y=ts_data["Tons"],
                                          mode='lines+markers', name="Original"),
                                row=1, col=1)
        # Trend component
        fig_combined.add_trace(go.Scatter(x=result.trend.index, y=result.trend,
                                          mode='lines+markers', name="Trend", line=dict(color="orange")),
                                row=2, col=1)
        # Seasonal component
        fig_combined.add_trace(go.Scatter(x=result.seasonal.index, y=result.seasonal,
                                          mode='lines+markers', name="Seasonal", line=dict(color="green")),
                                row=3, col=1)
        # Residual component
        fig_combined.add_trace(go.Scatter(x=result.resid.index, y=result.resid,
                                          mode='lines+markers', name="Residual", line=dict(color="red")),
                                row=4, col=1)
        fig_combined.update_layout(height=900, title_text="Time Series Decomposition", template="plotly_white")
        fig_combined.update_xaxes(title_text="Period", row=4, col=1)
        fig_combined.update_yaxes(title_text="Volume (Tons)", row=1, col=1)
        st.plotly_chart(fig_combined, use_container_width=True)
    
    st.success("✅ Time Series Decomposition completed successfully!")
