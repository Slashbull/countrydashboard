# detailed_analysis.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def detailed_analysis_dashboard(data: pd.DataFrame):
    st.title("🔍 Detailed Analysis Dashboard")
    
    # Validate required columns.
    required_cols = ["Reporter", "Partner", "Tons", "Year", "Month", "Period"]
    missing = [col for col in required_cols if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing required columns: {', '.join(missing)}")
        return

    # Ensure "Tons" is numeric.
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    
    # Create three main tabs.
    tabs = st.tabs(["Summary Metrics", "Reporters Breakdown", "Detailed Drilldown"])
    
    #########################################################
    # Tab 1: Summary Metrics – Overall KPIs
    #########################################################
    with tabs[0]:
        st.header("Overall Summary Metrics")
        total_volume = data["Tons"].sum()
        total_records = data.shape[0]
        avg_volume = total_volume / total_records if total_records > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Volume (Tons)", f"{total_volume:,.2f}")
        col1.metric("Total Records", total_records)
        col2.metric("Avg Volume/Record", f"{avg_volume:,.2f}")
        unique_partners = data["Partner"].nunique()
        col3.metric("Unique Partners", unique_partners)
        # Calculate MoM Growth.
        if "Period_dt" in data.columns:
            periods_sorted = data.sort_values("Period_dt")["Period"].unique()
        else:
            periods_sorted = data["Period"].unique()
        if len(periods_sorted) >= 2:
            last_period = periods_sorted[-1]
            second_last_period = periods_sorted[-2]
            vol_last = data[data["Period"] == last_period]["Tons"].sum()
            vol_prev = data[data["Period"] == second_last_period]["Tons"].sum()
            mom_growth = ((vol_last - vol_prev) / vol_prev * 100) if vol_prev != 0 else 0
        else:
            mom_growth = 0
        st.metric("MoM Growth (%)", f"{mom_growth:,.2f}")
        
        st.markdown("---")
        # Identify Top Reporter (for context)
        rep_summary = data.groupby("Reporter")["Tons"].sum().reset_index().sort_values("Tons", ascending=False)
        if not rep_summary.empty:
            top_reporter = rep_summary.iloc[0]["Reporter"]
            top_reporter_volume = rep_summary.iloc[0]["Tons"]
            top_reporter_share = (top_reporter_volume / total_volume * 100) if total_volume > 0 else 0
            st.markdown(f"**Top Reporter:** {top_reporter} ({top_reporter_share:,.2f}% of total volume)")
        else:
            st.info("No Reporter data available.")
        
        if "Period_dt" in data.columns:
            last_updated = data["Period_dt"].max().strftime("%b-%Y")
            st.info(f"Data last updated: {last_updated}")

    #########################################################
    # Tab 2: Reporters Breakdown
    #########################################################
    with tabs[1]:
        st.header("Reporters Breakdown")
        try:
            rep_breakdown = data.groupby("Reporter")["Tons"].sum().reset_index().sort_values("Tons", ascending=False)
            st.dataframe(rep_breakdown)
            fig_rep = px.bar(
                rep_breakdown,
                x="Reporter",
                y="Tons",
                title="Trade Volume by Reporter",
                text_auto=True,
                template="plotly_white"
            )
            st.plotly_chart(fig_rep, use_container_width=True)
        except Exception as e:
            st.error("Error generating Reporters Breakdown.")
            st.error(e)

    #########################################################
    # Tab 3: Detailed Drilldown Analysis
    #########################################################
    with tabs[2]:
        st.header("Detailed Drilldown Analysis")
        st.markdown("Select a dimension (Reporter or Partner) and apply a date range filter for granular insights.")
        
        # Let the user choose which dimension to drill down on.
        dimension = st.radio("Select Dimension for Drilldown:", ("Reporter", "Partner"), index=0)
        entities = sorted(data[dimension].dropna().unique().tolist())
        if not entities:
            st.error(f"No data available for dimension: {dimension}")
            return
        selected_entity = st.selectbox(f"Select {dimension}:", entities)
        
        # Filter data by selected entity.
        detail_data = data[data[dimension] == selected_entity]
        
        # If a datetime column is available, add a date range filter.
        if "Period_dt" in detail_data.columns:
            min_date = detail_data["Period_dt"].min().date()
            max_date = detail_data["Period_dt"].max().date()
            date_range = st.date_input("Select Date Range:", value=[min_date, max_date])
            if isinstance(date_range, list) and len(date_range) == 2:
                start_date, end_date = date_range
                detail_data = detail_data[(detail_data["Period_dt"].dt.date >= start_date) & 
                                          (detail_data["Period_dt"].dt.date <= end_date)]
        
        if detail_data.empty:
            st.error("No data available for the selected filters.")
            return
        
        st.subheader(f"Trade Data for {dimension}: {selected_entity}")
        st.dataframe(detail_data)
        
        # Download button for drilldown data.
        csv_download = detail_data.to_csv(index=False).encode("utf-8")
        st.download_button("Download Detailed Data as CSV", csv_download, "drilldown_data.csv", "text/csv")
        
        st.markdown("##### Key Metrics for Selected Entity")
        entity_total = detail_data["Tons"].sum()
        entity_count = detail_data.shape[0]
        unique_periods = detail_data["Period"].nunique() if "Period" in detail_data.columns else 1
        entity_avg = entity_total / unique_periods if unique_periods > 0 else 0
        # Calculate MoM growth for selected entity.
        periods = sorted(detail_data["Period"].unique())
        if len(periods) >= 2:
            last_p = periods[-1]
            second_last_p = periods[-2]
            vol_last = detail_data[detail_data["Period"] == last_p]["Tons"].sum()
            vol_prev = detail_data[detail_data["Period"] == second_last_p]["Tons"].sum()
            entity_mom = ((vol_last - vol_prev) / vol_prev * 100) if vol_prev != 0 else 0
        else:
            entity_mom = 0
        
        colA, colB, colC, colD = st.columns(4)
        colA.metric("Total Volume", f"{entity_total:,.2f} Tons")
        colB.metric("Transactions", entity_count)
        colC.metric("Avg Volume/Period", f"{entity_avg:,.2f} Tons")
        colD.metric("MoM Growth (%)", f"{entity_mom:,.2f}")
        
        st.markdown("---")
        st.markdown("##### Pivot Table: Volume by Period")
        try:
            pivot = detail_data.pivot_table(
                index=dimension,
                columns="Period",
                values="Tons",
                aggfunc="sum",
                fill_value=0
            )
            st.dataframe(pivot)
        except Exception as e:
            st.error("Error generating pivot table.")
            st.error(e)
        
        st.markdown("---")
        st.markdown("##### Trade Volume Trend")
        try:
            trend_data = detail_data.groupby("Period", as_index=False)["Tons"].sum()
            if "Period_dt" in detail_data.columns:
                period_map = detail_data.drop_duplicates("Period")[["Period", "Period_dt"]]
                trend_data = pd.merge(trend_data, period_map, on="Period", how="left")
                trend_data = trend_data.sort_values("Period_dt")
            else:
                trend_data = trend_data.sort_values("Period")
            
            fig_trend = px.line(
                trend_data,
                x="Period",
                y="Tons",
                title=f"Trade Volume Trend for {selected_entity}",
                markers=True,
                template="plotly_white"
            )
            # Option to overlay a rolling average.
            if st.checkbox("Show 3-Period Rolling Average", key="rolling_avg"):
                trend_data["Rolling_Avg"] = trend_data["Tons"].rolling(window=3, min_periods=1).mean()
                fig_trend.add_trace(
                    go.Scatter(
                        x=trend_data["Period"],
                        y=trend_data["Rolling_Avg"],
                        mode="lines+markers",
                        name="Rolling Average",
                        line=dict(dash="dash", color="red")
                    )
                )
            # Add annotations for max and min values.
            if not trend_data.empty:
                max_row = trend_data.loc[trend_data["Tons"].idxmax()]
                min_row = trend_data.loc[trend_data["Tons"].idxmin()]
                fig_trend.add_annotation(
                    x=max_row["Period"],
                    y=max_row["Tons"],
                    text=f"Max: {max_row['Tons']:,.2f}",
                    showarrow=True,
                    arrowhead=2,
                    ax=0,
                    ay=-30
                )
                fig_trend.add_annotation(
                    x=min_row["Period"],
                    y=min_row["Tons"],
                    text=f"Min: {min_row['Tons']:,.2f}",
                    showarrow=True,
                    arrowhead=2,
                    ax=0,
                    ay=30
                )
            fig_trend.update_layout(xaxis_title="Period", yaxis_title="Volume (Tons)")
            st.plotly_chart(fig_trend, use_container_width=True)
        except Exception as e:
            st.error("Error generating trend chart.")
            st.error(e)
        
        st.success("Detailed Drilldown loaded successfully!")
    
    st.success("✅ Detailed Analysis Dashboard loaded successfully!")
