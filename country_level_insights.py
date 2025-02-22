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
    Explore trade volume aggregated by Partner.
    
    Use the tabs below to view an overview, detailed trend analysis, and download the aggregated data.
    """)

    # Fixed dimension: Partner.
    dimension = "Partner"
    if dimension not in data.columns:
        st.error(f"🚨 The selected dimension '{dimension}' is missing from the data.")
        return

    # Ensure "Tons" is numeric.
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")

    # Aggregate data by Partner.
    agg_data = data.groupby(dimension, as_index=False)["Tons"].sum()
    agg_data = agg_data.sort_values("Tons", ascending=False)
    total_volume = agg_data["Tons"].sum()

    # Apply clustering.
    agg_data = apply_clustering(agg_data)

    # ISO mapping (for potential future expansion).
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
    tabs = st.tabs(["Overview", "Trend Analysis", "Download Data"])
    
    #########################################################
    # Tab 1: Overview – Aggregated Data & Visualizations
    #########################################################
    with tabs[0]:
        st.header("Overview by Partner")
        st.markdown("#### Aggregated Data Table")
        st.dataframe(agg_data)

        st.markdown("#### Bar Chart: Trade Volume by Partner")
        fig_bar = px.bar(
            agg_data,
            x=dimension,
            y="Tons",
            color="cluster",
            title="Trade Volume by Partner (Clustered)",
            labels={"Tons": "Volume (Tons)"},
            text_auto=True,
            template="plotly_white"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("#### Donut Chart: Market Share by Partner")
        agg_data["Share (%)"] = (agg_data["Tons"] / total_volume) * 100
        fig_donut = px.pie(
            agg_data,
            names=dimension,
            values="Tons",
            title="Market Share by Partner",
            hole=0.4,
            hover_data={"Share (%)":":.2f"},
            template="plotly_white"
        )
        st.plotly_chart(fig_donut, use_container_width=True)
    
    #########################################################
    # Tab 2: Trend Analysis – Multiple Trend Visualizations
    #########################################################
    with tabs[1]:
        st.header("Trend Analysis")
        if "Period" not in data.columns or "Year" not in data.columns:
            st.info("Both 'Period' and 'Year' columns are required for detailed trend analysis.")
        else:
            # --- Overall Trends (aggregated across all data) ---
            st.subheader("Overall Monthly Trend")
            overall_monthly = data.groupby("Period")["Tons"].sum().reset_index().sort_values("Period")
            fig_overall_month = px.line(
                overall_monthly,
                x="Period",
                y="Tons",
                title="Overall Monthly Trade Volume Trend",
                markers=True,
                template="plotly_white"
            )
            fig_overall_month.update_layout(xaxis_title="Period", yaxis_title="Volume (Tons)")
            st.plotly_chart(fig_overall_month, use_container_width=True)
            
            st.markdown("---")
            st.subheader("Overall Yearly Trend")
            overall_yearly = data.groupby("Year")["Tons"].sum().reset_index().sort_values("Year")
            fig_overall_year = px.line(
                overall_yearly,
                x="Year",
                y="Tons",
                title="Overall Yearly Trade Volume Trend",
                markers=True,
                template="plotly_white"
            )
            fig_overall_year.update_layout(xaxis_title="Year", yaxis_title="Volume (Tons)")
            st.plotly_chart(fig_overall_year, use_container_width=True)

            st.markdown("---")
            # --- Detailed Trends for a Selected Partner ---
            # Create a new column "Month_Abbr" from the Period column (assumed format "Jan-2012").
            if "Month_Abbr" not in data.columns:
                data["Month_Abbr"] = data["Period"].apply(lambda x: x.split("-")[0])
            # Order the Month_Abbr.
            data["Month_Abbr"] = pd.Categorical(data["Month_Abbr"], categories=list(MONTH_ORDER.keys()), ordered=True)

            st.subheader("Monthly Trend (by Year) for Selected Partner")
            selected_partner = st.selectbox("Select a Partner for Detailed Trend Analysis:", agg_data[dimension].unique())
            entity_data = data[data[dimension] == selected_partner]
            if entity_data.empty:
                st.info(f"No trend data available for {selected_partner}.")
            else:
                fig_multiline = px.line(
                    entity_data,
                    x="Month_Abbr",
                    y="Tons",
                    color="Year",
                    title=f"Monthly Trend for {selected_partner} by Year",
                    markers=True,
                    template="plotly_white"
                )
                fig_multiline.update_layout(xaxis_title="Month", yaxis_title="Volume (Tons)")
                st.plotly_chart(fig_multiline, use_container_width=True)

                st.markdown("---")
                st.subheader("Yearly Trend by Month for Selected Partner")
                yearly_by_month = entity_data.groupby(["Year", "Month_Abbr"], as_index=False)["Tons"].sum()
                if yearly_by_month.empty:
                    st.info("No data available for Yearly Trend by Month.")
                else:
                    fig_yearly = px.line(
                        yearly_by_month,
                        x="Year",
                        y="Tons",
                        color="Month_Abbr",
                        title=f"Yearly Trend by Month for {selected_partner}",
                        markers=True,
                        template="plotly_white"
                    )
                    fig_yearly.update_layout(xaxis_title="Year", yaxis_title="Volume (Tons)")
                    st.plotly_chart(fig_yearly, use_container_width=True)
    
    #########################################################
    # Tab 3: Download Data
    #########################################################
    with tabs[2]:
        st.header("Download Aggregated Data")
        csv_data = agg_data.to_csv(index=False).encode("utf-8")
        st.download_button("Download Data as CSV", csv_data, "aggregated_data.csv", "text/csv")
    
    st.success("✅ Country-Level Insights Dashboard loaded successfully!")
