# country_level_insights.py
import streamlit as st
import pandas as pd
import plotly.express as px

def country_level_insights_dashboard(data: pd.DataFrame):
    st.title("🌍 Country-Level Insights Dashboard")
    st.markdown("""
    Explore trade volume aggregated by a chosen dimension.  
    Use the tabs below to view an overview, trend analysis, geographic distribution (if applicable), and download the aggregated data.
    """)

    # Allow user to choose the dimension for aggregation.
    dimension = st.radio("Select Dimension for Aggregation:", ("Reporter", "Partner"), index=0)
    if dimension not in data.columns:
        st.error(f"🚨 The selected dimension '{dimension}' is missing from the data.")
        return

    # Ensure "Tons" is numeric.
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")

    # Aggregate data by the selected dimension.
    agg_data = data.groupby(dimension, as_index=False)["Tons"].sum()
    agg_data = agg_data.sort_values("Tons", ascending=False)
    total_volume = agg_data["Tons"].sum()

    # --- ISO Mapping for Geographic Distribution ---
    # Default ISO mapping for country-level (Reporter) analysis.
    # For Partner analysis, if no mapping is provided, we will display an informative message.
    iso_mapping = {
        "India": "IND",
        "USA": "USA",
        "China": "CHN",
        "Germany": "DEU",
        "Brazil": "BRA",
        "United Kingdom": "GBR",
        "France": "FRA",
        "Canada": "CAN"
        # Extend this mapping as needed.
    }
    if dimension == "Reporter":
        agg_data["iso_alpha"] = agg_data[dimension].map(iso_mapping)
    else:
        # For Partner dimension, we don't have a default mapping.
        agg_data["iso_alpha"] = None

    # Create a multi-tab layout.
    tabs = st.tabs(["Overview", "Trend Analysis", "Geographic Distribution", "Download Data"])
    
    #########################################################
    # Tab 1: Overview – Aggregated Data & Visualizations
    #########################################################
    with tabs[0]:
        st.header(f"Overview by {dimension}")
        st.markdown("#### Aggregated Data Table")
        st.dataframe(agg_data)

        st.markdown(f"#### Bar Chart: Trade Volume by {dimension}")
        fig_bar = px.bar(
            agg_data,
            x=dimension,
            y="Tons",
            title=f"Trade Volume by {dimension}",
            labels={"Tons": "Volume (Tons)"},
            text_auto=True,
            template="plotly_white"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown(f"#### Donut Chart: Market Share by {dimension}")
        agg_data["Share (%)"] = (agg_data["Tons"] / total_volume) * 100
        fig_donut = px.pie(
            agg_data,
            names=dimension,
            values="Tons",
            title=f"Market Share by {dimension}",
            hole=0.4,
            hover_data={"Share (%)":":.2f"},
            template="plotly_white"
        )
        st.plotly_chart(fig_donut, use_container_width=True)
    
    #########################################################
    # Tab 2: Trend Analysis – Time Series Visualization
    #########################################################
    with tabs[1]:
        st.header("Trend Analysis")
        if "Period" not in data.columns:
            st.info("No 'Period' column available for time series analysis.")
        else:
            trend_data = data.groupby(["Period", dimension])["Tons"].sum().reset_index()
            selected_entity = st.selectbox(f"Select a {dimension} for Trend Analysis:", agg_data[dimension].unique())
            trend_entity = trend_data[trend_data[dimension] == selected_entity]
            if trend_entity.empty:
                st.info(f"No trend data available for {selected_entity}.")
            else:
                fig_trend = px.line(
                    trend_entity,
                    x="Period",
                    y="Tons",
                    title=f"Trade Volume Trend for {selected_entity}",
                    markers=True,
                    template="plotly_white"
                )
                fig_trend.update_layout(xaxis_title="Period", yaxis_title="Volume (Tons)")
                st.plotly_chart(fig_trend, use_container_width=True)
    
    #########################################################
    # Tab 3: Geographic Distribution – Choropleth Map
    #########################################################
    with tabs[2]:
        st.header("Geographic Distribution")
        if dimension == "Partner":
            st.info("Geographic distribution visualization is currently only available for Reporter-based analysis. " +
                    "Please switch to Reporter dimension or update the ISO mapping for partners.")
        else:
            if agg_data["iso_alpha"].isnull().all():
                st.info("No ISO country codes available for the selected dimension. " +
                        "Please update the ISO mapping for Reporter analysis.")
            else:
                fig_map = px.choropleth(
                    agg_data.dropna(subset=["iso_alpha"]),
                    locations="iso_alpha",
                    color="Tons",
                    hover_name=dimension,
                    color_continuous_scale=px.colors.sequential.Plasma,
                    title=f"Trade Volume by {dimension} (Geographic View)"
                )
                st.plotly_chart(fig_map, use_container_width=True)

    #########################################################
    # Tab 4: Download Data
    #########################################################
    with tabs[3]:
        st.header("Download Aggregated Data")
        csv_data = agg_data.to_csv(index=False).encode("utf-8")
        st.download_button("Download Data as CSV", csv_data, "aggregated_data.csv", "text/csv")
    
    st.success("✅ Country-Level Insights Dashboard loaded successfully!")
