import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from prophet import Prophet
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime

# Helper function for automated insights
def generate_insights(data, dimension):
    insights = []
    top_country = data[dimension].iloc[0]
    top_volume = data["Tons"].iloc[0]
    total_volume = data["Tons"].sum()
    share = (top_volume / total_volume) * 100
    insights.append(f"🔍 **{top_country}** has the highest trade volume at **{top_volume:,.0f} tons**, accounting for **{share:.2f}%** of the total.")
    
    # Anomaly detection
    clf = IsolationForest(contamination=0.05)
    data["anomaly"] = clf.fit_predict(data[["Tons"]])
    anomalies = data[data["anomaly"] == -1]
    if not anomalies.empty:
        insights.append("🚨 **Anomalies Detected**: The following countries have unusual trade volumes:")
        insights.append(anomalies[[dimension, "Tons"]].to_markdown(index=False))
    
    return "\n\n".join(insights)

# Helper function for clustering
def apply_clustering(data, n_clusters=3):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    data["cluster"] = kmeans.fit_predict(data[["Tons"]])
    return data

# Helper function for time series forecasting
def forecast_trend(data, entity, dimension):
    df = data[data[dimension] == entity][["Period", "Tons"]].rename(columns={"Period": "ds", "Tons": "y"})
    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=12, freq="M")
    forecast = model.predict(future)
    return forecast, model

def country_level_insights_dashboard(data: pd.DataFrame):
    st.title("🌍 Advanced Country-Level Insights Dashboard")
    st.markdown("""
    Explore trade volume with advanced analytics, visualizations, and automated insights.
    """)

    # Ensure "Tons" is numeric
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")

    # Allow user to choose the dimension for aggregation
    dimension = st.radio("Select Dimension for Aggregation:", ("Reporter", "Partner"), index=0)
    if dimension not in data.columns:
        st.error(f"🚨 The selected dimension '{dimension}' is missing from the data.")
        return

    # Aggregate data by the selected dimension
    agg_data = data.groupby(dimension, as_index=False)["Tons"].sum()
    agg_data = agg_data.sort_values("Tons", ascending=False)
    total_volume = agg_data["Tons"].sum()

    # Apply clustering
    agg_data = apply_clustering(agg_data)

    # ISO Mapping for Geographic Distribution
    iso_mapping = {
        "INDIA": "IND", "USA": "USA", "CHINA": "CHN", "GERMANY": "DEU", "BRAZIL": "BRA",
        "UNITED KINGDOM": "GBR", "FRANCE": "FRA", "CANADA": "CAN", "IRAQ": "IRQ",
        "UAE": "ARE", "IRAN": "IRN", "SAUDI ARABIA": "SAU", "TUNISIA": "TUN",
        "ALGERIA": "DZA", "ISRAEL": "ISR", "JORDAN": "JOR", "STATE OF PALESTINE": "PSE"
    }
    agg_data["iso_alpha"] = agg_data[dimension].str.upper().map(iso_mapping)

    # Create a multi-tab layout
    tabs = st.tabs(["Overview", "Trend Analysis", "Geographic Distribution", "Network Analysis", "Download Data"])

    #########################################################
    # Tab 1: Overview – Aggregated Data & Visualizations
    #########################################################
    with tabs[0]:
        st.header(f"Overview by {dimension}")
        st.markdown("#### Automated Insights")
        st.markdown(generate_insights(agg_data, dimension))

        st.markdown("#### Aggregated Data Table")
        st.dataframe(agg_data)

        st.markdown(f"#### Bar Chart: Trade Volume by {dimension}")
        fig_bar = px.bar(
            agg_data,
            x=dimension,
            y="Tons",
            color="cluster",
            title=f"Trade Volume by {dimension} (Clustered)",
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
                # Time Series Forecasting
                forecast, model = forecast_trend(trend_data, selected_entity, dimension)
                fig_trend = go.Figure()
                fig_trend.add_trace(go.Scatter(x=trend_entity["Period"], y=trend_entity["Tons"], name="Actual"))
                fig_trend.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat"], name="Forecast"))
                fig_trend.update_layout(
                    title=f"Trade Volume Trend for {selected_entity} (Forecast)",
                    xaxis_title="Period",
                    yaxis_title="Volume (Tons)",
                    template="plotly_white"
                )
                st.plotly_chart(fig_trend, use_container_width=True)

    #########################################################
    # Tab 3: Geographic Distribution – Enhanced Choropleth Map
    #########################################################
    with tabs[2]:
        st.header("Geographic Distribution")
        if agg_data["iso_alpha"].isnull().all():
            st.info("No ISO country codes available for the selected dimension.")
        else:
            fig_map = px.choropleth(
                agg_data.dropna(subset=["iso_alpha"]),
                locations="iso_alpha",
                color="Tons",
                hover_name=dimension,
                color_continuous_scale=px.colors.sequential.Plasma,
                title=f"Trade Volume by {dimension} (Geographic View)",
                labels={"Tons": "Volume (Tons)"}
            )
            fig_map.update_geos(
                showcoastlines=True,
                coastlinecolor="RebeccaPurple",
                showland=True,
                landcolor="LightGreen",
                showocean=True,
                oceancolor="LightBlue",
                projection_type="equirectangular"
            )
            fig_map.update_layout(
                margin=dict(l=0, r=0, t=50, b=0),
                title_font=dict(size=20)
            )
            st.plotly_chart(fig_map, use_container_width=True)

    #########################################################
    # Tab 4: Network Analysis – Trade Relationships
    #########################################################
    with tabs[3]:
        st.header("Network Analysis")
        G = nx.from_pandas_edgelist(data, source="Reporter", target="Partner", edge_attr="Tons")
        pos = nx.spring_layout(G)
        fig, ax = plt.subplots(figsize=(10, 8))
        nx.draw(G, pos, with_labels=True, node_size=2000, node_color="skyblue", font_size=10, ax=ax)
        st.pyplot(fig)

    #########################################################
    # Tab 5: Download Data
    #########################################################
    with tabs[4]:
        st.header("Download Aggregated Data")
        csv_data = agg_data.to_csv(index=False).encode("utf-8")
        st.download_button("Download Data as CSV", csv_data, "aggregated_data.csv", "text/csv")

    st.success("✅ Advanced Country-Level Insights Dashboard loaded successfully!")
