# country_level_insights.py
import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans

# Helper function for clustering with safety checks.
def apply_clustering(data: pd.DataFrame, n_clusters=3):
    """
    Apply KMeans clustering on the 'Tons' column.
    If there are fewer samples than n_clusters, assign all to cluster 0.
    """
    if data.shape[0] < n_clusters:
        data["cluster"] = 0
        return data
    try:
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        if data["Tons"].isnull().any():
            data = data.dropna(subset=["Tons"])
        data["cluster"] = kmeans.fit_predict(data[["Tons"]])
    except Exception as e:
        st.warning("Clustering failed, assigning default cluster.")
        data["cluster"] = 0
    return data

# Helper dictionary to order months.
MONTH_ORDER = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

def country_level_insights_dashboard(data: pd.DataFrame):
    st.title("🌍 Country-Level Insights Dashboard")
    st.markdown("""
    Explore trade volume aggregated by a chosen dimension.
    
    Use the tabs below to view an overview, trend analysis, geographic distribution, and download the aggregated data.
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

    # Apply clustering.
    agg_data = apply_clustering(agg_data)

    # --- ISO Mapping for Geographic Distribution ---
    if dimension == "Reporter":
        iso_mapping = {
            "INDIA": "IND",
            "USA": "USA",
            "CHINA": "CHN",
            "GERMANY": "DEU",
            "BRAZIL": "BRA",
            "UNITED KINGDOM": "GBR",
            "FRANCE": "FRA",
            "CANADA": "CAN"
            # Extend as needed.
        }
    else:  # For Partner dimension.
        iso_mapping = {
            "IRAQ": "IRQ",
            "UAE": "ARE",
            "UNITED ARAB EMIRATES": "ARE",
            "IRAN": "IRN",
            "SAUDI ARABIA": "SAU",
            "TUNISIA": "TUN",
            "ALGERIA": "DZA",
            "ISRAEL": "ISR",
            "JORDAN": "JOR",
            "STATE OF PALESTINE": "PSE"
        }
    agg_data["iso_alpha"] = agg_data[dimension].str.upper().map(iso_mapping)

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
    # Tab 2: Trend Analysis – Monthly & Yearly Visualization
    #########################################################
    with tabs[1]:
        st.header("Trend Analysis")
        if "Period" not in data.columns or "Year" not in data.columns:
            st.info("Both 'Period' and 'Year' columns are required for detailed trend analysis.")
        else:
            # Ensure Month abbreviation is extracted.
            if "Month_Abbr" not in data.columns:
                data["Month_Abbr"] = data["Period"].apply(lambda x: x.split("-")[0])
            # Order the Month_Abbr.
            data["Month_Abbr"] = pd.Categorical(data["Month_Abbr"], categories=list(MONTH_ORDER.keys()), ordered=True)

            # Let the user select an entity for trend analysis.
            selected_entity = st.selectbox(f"Select a {dimension} for Trend Analysis:", agg_data[dimension].unique())
            entity_data = data[data[dimension] == selected_entity]
            if entity_data.empty:
                st.info(f"No trend data available for {selected_entity}.")
            else:
                st.subheader("Monthly Trend (by Year)")
                # Multi-line chart with x-axis = Month_Abbr and line color = Year.
                fig_multiline = px.line(
                    entity_data,
                    x="Month_Abbr",
                    y="Tons",
                    color="Year",
                    title=f"Monthly Trend for {selected_entity} by Year",
                    markers=True,
                    template="plotly_white"
                )
                fig_multiline.update_layout(xaxis_title="Month", yaxis_title="Volume (Tons)")
                st.plotly_chart(fig_multiline, use_container_width=True)

                st.subheader("Yearly Trend by Month")
                # Here, pivot the data: x-axis = Year, and create a line for each month.
                yearly_by_month = entity_data.groupby(["Year", "Month_Abbr"], as_index=False)["Tons"].sum()
                if yearly_by_month.empty:
                    st.info("No data available for Yearly Trend by Month.")
                else:
                    fig_yearly = px.line(
                        yearly_by_month,
                        x="Year",
                        y="Tons",
                        color="Month_Abbr",
                        title=f"Yearly Trend by Month for {selected_entity}",
                        markers=True,
                        template="plotly_white"
                    )
                    fig_yearly.update_layout(xaxis_title="Year", yaxis_title="Volume (Tons)")
                    st.plotly_chart(fig_yearly, use_container_width=True)
    
    #########################################################
    # Tab 3: Geographic Distribution – Enhanced Choropleth Map
    #########################################################
    with tabs[2]:
        st.header("Geographic Distribution")
        if agg_data["iso_alpha"].isnull().all():
            st.info("No ISO country codes available for the selected dimension. " +
                    "For Reporter analysis, update the ISO mapping if necessary. " +
                    "For Partner analysis, please update the mapping in the code.")
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
    # Tab 4: Download Data
    #########################################################
    with tabs[3]:
        st.header("Download Aggregated Data")
        csv_data = agg_data.to_csv(index=False).encode("utf-8")
        st.download_button("Download Data as CSV", csv_data, "aggregated_data.csv", "text/csv")
    
    st.success("✅ Country-Level Insights Dashboard loaded successfully!")
