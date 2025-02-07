# market_overview.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def market_overview_dashboard(data: pd.DataFrame):
    st.title("📊 Market Overview Dashboard")
    
    # --- Validate required columns ---
    required_columns = ["SR NO.", "Year", "Month", "Reporter", "Flow", "Partner", "Code", "Desc", "Tons"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    # Convert Tons column to numeric.
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    
    # Use filtered data if available (set in st.session_state by the filters module), otherwise use raw data.
    filtered_data = st.session_state.get("filtered_data", data).copy()
    
    # --- Create the 'Period' column if not already present ---
    if "Period" not in filtered_data.columns:
        try:
            # Define a helper function to parse Month and Year.
            def parse_period(row):
                month_val = row["Month"]
                year_val = str(row["Year"])
                # If month is numeric, assume month number; otherwise, assume abbreviated text.
                if str(month_val).isdigit():
                    return datetime.strptime(f"{int(month_val)} {year_val}", "%m %Y")
                else:
                    return datetime.strptime(f"{month_val} {year_val}", "%b %Y")
            filtered_data["Period_dt"] = filtered_data.apply(parse_period, axis=1)
            # Create a sorted list of period labels.
            sorted_periods = sorted(filtered_data["Period_dt"].dropna().unique())
            period_labels = [dt.strftime("%b-%Y") for dt in sorted_periods]
            filtered_data["Period"] = filtered_data["Period_dt"].dt.strftime("%b-%Y")
            # Make 'Period' a categorical with proper ordering.
            filtered_data["Period"] = pd.Categorical(filtered_data["Period"], categories=period_labels, ordered=True)
        except Exception as e:
            st.error("Error creating 'Period' column. Please check the Month and Year formats.")
            st.error(e)
            return

    # --- Dashboard Layout with Tabs ---
    tabs = st.tabs(["Summary", "Trends", "Breakdown", "Detailed Analysis"])

    ### Tab 1: Summary
    with tabs[0]:
        st.header("Key Performance Indicators")
        total_volume = filtered_data["Tons"].sum()
        unique_partners = filtered_data["Partner"].nunique()
        unique_reporters = filtered_data["Reporter"].nunique()
        avg_volume = total_volume / unique_partners if unique_partners > 0 else 0

        # Calculate Month-over-Month (MoM) growth using the sorted Periods.
        if "Period_dt" in filtered_data.columns:
            periods_sorted = filtered_data.sort_values("Period_dt")["Period"].unique()
        else:
            periods_sorted = filtered_data["Period"].unique()
        if len(periods_sorted) >= 2:
            last_period = periods_sorted[-1]
            second_last_period = periods_sorted[-2]
            vol_last = filtered_data[filtered_data["Period"] == last_period]["Tons"].sum()
            vol_prev = filtered_data[filtered_data["Period"] == second_last_period]["Tons"].sum()
            mom_growth = ((vol_last - vol_prev) / vol_prev * 100) if vol_prev != 0 else 0
        else:
            mom_growth = 0

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Volume (Tons)", f"{total_volume:,.2f}")
        col2.metric("Unique Partners", unique_partners)
        col3.metric("Unique Reporters", unique_reporters)
        col4.metric("Avg Volume/Partner", f"{avg_volume:,.2f}")
        col5.metric("MoM Growth (%)", f"{mom_growth:,.2f}")

        st.markdown("---")
        st.subheader("Market Share by Partner")
        partner_summary = filtered_data.groupby("Partner", as_index=False)["Tons"].sum()
        partner_summary["Percentage"] = (partner_summary["Tons"] / partner_summary["Tons"].sum()) * 100
        fig_donut = px.pie(partner_summary, names="Partner", values="Tons", 
                           title="Market Share by Partner", hole=0.4,
                           hover_data={"Percentage":":.2f"})
        st.plotly_chart(fig_donut, use_container_width=True)

    ### Tab 2: Trends
    with tabs[1]:
        st.header("Monthly & Yearly Trends")
        # --- Monthly Trends ---
        if "Period_dt" in filtered_data.columns:
            monthly_trends = filtered_data.groupby(["Period", "Period_dt"], as_index=False)["Tons"].sum()
            monthly_trends = monthly_trends.sort_values("Period_dt")
        else:
            monthly_trends = filtered_data.groupby("Period", as_index=False)["Tons"].sum()
            monthly_trends = monthly_trends.sort_values("Period")
        fig_line = px.line(monthly_trends, x="Period", y="Tons", 
                           title="Monthly Trade Volume Trend", markers=True)
        fig_line.update_layout(
            autosize=True,
            margin=dict(l=40, r=40, t=40, b=40),
            xaxis_title="Period",
            yaxis_title="Volume (Tons)"
        )
        st.plotly_chart(fig_line, use_container_width=True)
        
        st.markdown("---")
        # --- Yearly Trends ---
        if "Year" in filtered_data.columns:
            yearly_trends = filtered_data.groupby("Year", as_index=False)["Tons"].sum()
            fig_year = px.bar(yearly_trends, x="Year", y="Tons", 
                              title="Yearly Trade Volume", text_auto=True)
            fig_year.update_layout(
                autosize=True,
                margin=dict(l=40, r=40, t=40, b=40),
                xaxis_title="Year",
                yaxis_title="Volume (Tons)"
            )
            st.plotly_chart(fig_year, use_container_width=True)
        else:
            st.info("Year information not available.")

    ### Tab 3: Breakdown
    with tabs[2]:
        st.header("Breakdown Analysis")
        # Removed Top 5 Reporters chart as requested.
        st.subheader("Top 5 Partners")
        partner_top = (filtered_data.groupby("Partner", as_index=False)["Tons"]
                       .sum().sort_values("Tons", ascending=False).head(5))
        fig_partner = px.bar(partner_top, x="Partner", y="Tons",
                             title="Top 5 Partners by Volume", text_auto=True)
        st.plotly_chart(fig_partner, use_container_width=True)
        
        # Additional breakdown: Distribution by Flow (if available)
        if "Flow" in filtered_data.columns:
            st.subheader("Volume Distribution by Flow")
            flow_summary = filtered_data.groupby("Flow", as_index=False)["Tons"].sum()
            fig_flow = px.pie(flow_summary, names="Flow", values="Tons", 
                              title="Volume Distribution by Flow", hole=0.4)
            st.plotly_chart(fig_flow, use_container_width=True)

    ### Tab 4: Detailed Analysis
    with tabs[3]:
        st.header("Detailed Analysis")
        st.markdown("Drill down into the data for granular insights.")
        # Let the user choose the dimension for detailed analysis.
        dimension = st.radio("Select Dimension for Detailed Analysis:", ("Partner", "Reporter"), index=0)
        entities = sorted(filtered_data[dimension].dropna().unique().tolist())
        selected_entity = st.selectbox(f"Select {dimension}:", entities)
        detailed_data = filtered_data[filtered_data[dimension] == selected_entity]
        st.subheader(f"Trade Data for {dimension}: {selected_entity}")
        st.dataframe(detailed_data)
        
        st.markdown("##### Pivot Table: Volume by Period")
        pivot = detailed_data.pivot_table(index=dimension, columns="Period", values="Tons", aggfunc="sum", fill_value=0)
        st.dataframe(pivot)
        
        st.markdown("##### Trend Analysis")
        entity_trend = detailed_data.groupby("Period", as_index=False)["Tons"].sum()
        # Ensure trend chart is sorted by period using Period_dt if available.
        if "Period_dt" in detailed_data.columns:
            # Merge with unique period_dt for proper sorting.
            period_map = detailed_data.drop_duplicates("Period")[["Period", "Period_dt"]]
            entity_trend = pd.merge(entity_trend, period_map, on="Period", how="left")
            entity_trend = entity_trend.sort_values("Period_dt")
        else:
            entity_trend = entity_trend.sort_values("Period")
        fig_entity = px.line(entity_trend, x="Period", y="Tons", 
                             title=f"Trade Volume Trend for {selected_entity}", markers=True)
        st.plotly_chart(fig_entity, use_container_width=True)
        st.success("Detailed Analysis loaded successfully!")
    
    st.success("✅ Market Overview Dashboard loaded successfully!")
