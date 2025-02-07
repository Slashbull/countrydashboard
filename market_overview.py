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
    
    # Use filtered data if available; otherwise, use raw data.
    df = st.session_state.get("filtered_data", data).copy()

    # --- Create the 'Period' column if not already present ---
    if "Period" not in df.columns:
        try:
            # Helper function: parse Month & Year into a datetime object.
            def parse_period(row):
                month_val = row["Month"]
                year_val = str(row["Year"])
                # Check if the Month is numeric or text
                if str(month_val).isdigit():
                    return datetime.strptime(f"{int(month_val)} {year_val}", "%m %Y")
                else:
                    return datetime.strptime(f"{month_val} {year_val}", "%b %Y")
            df["Period_dt"] = df.apply(parse_period, axis=1)
            # Build sorted period labels
            sorted_dt = sorted(df["Period_dt"].dropna().unique())
            period_labels = [dt.strftime("%b-%Y") for dt in sorted_dt]
            df["Period"] = df["Period_dt"].dt.strftime("%b-%Y")
            # Set as categorical so that charts order correctly.
            df["Period"] = pd.Categorical(df["Period"], categories=period_labels, ordered=True)
        except Exception as e:
            st.error("Error creating 'Period' column. Please check the Month and Year formats.")
            st.error(e)
            return

    # --- Dashboard Layout using Tabs ---
    tabs = st.tabs(["Summary", "Trends", "Breakdown", "Detailed Analysis"])

    ### TAB 1: SUMMARY
    with tabs[0]:
        st.header("Key Performance Indicators")
        total_volume = df["Tons"].sum()
        unique_partners = df["Partner"].nunique()
        unique_reporters = df["Reporter"].nunique()
        avg_volume = total_volume / unique_partners if unique_partners > 0 else 0

        # Calculate Month-over-Month (MoM) growth:
        periods = df.sort_values("Period_dt")["Period"].unique()
        if len(periods) >= 2:
            last_period = periods[-1]
            second_last_period = periods[-2]
            vol_last = df[df["Period"] == last_period]["Tons"].sum()
            vol_prev = df[df["Period"] == second_last_period]["Tons"].sum()
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
        partner_summary = df.groupby("Partner", as_index=False)["Tons"].sum()
        partner_summary["Percentage"] = (partner_summary["Tons"] / partner_summary["Tons"].sum()) * 100
        fig_donut = px.pie(
            partner_summary,
            names="Partner",
            values="Tons",
            title="Market Share by Partner",
            hole=0.4,
            hover_data={"Percentage":":.2f"}
        )
        fig_donut.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_donut, use_container_width=True)

    ### TAB 2: TRENDS
    with tabs[1]:
        st.header("Monthly & Yearly Trends")
        # Monthly Trends: Group by Period and use the datetime column for sorting.
        monthly_trends = df.groupby(["Period", "Period_dt"], as_index=False)["Tons"].sum().sort_values("Period_dt")
        fig_line = px.line(
            monthly_trends,
            x="Period",
            y="Tons",
            title="Monthly Trade Volume Trend",
            markers=True
        )
        fig_line.update_layout(
            xaxis=dict(title="Period", tickangle=-45),
            yaxis=dict(title="Volume (Tons)"),
            margin=dict(l=40, r=40, t=40, b=80),
            template="plotly_white"
        )
        st.plotly_chart(fig_line, use_container_width=True)

        st.markdown("---")
        # Yearly Trends: Sum volume by Year.
        if "Year" in df.columns:
            yearly_trends = df.groupby("Year", as_index=False)["Tons"].sum().sort_values("Year")
            fig_year = px.bar(
                yearly_trends,
                x="Year",
                y="Tons",
                title="Yearly Trade Volume",
                text_auto=True
            )
            fig_year.update_layout(
                xaxis_title="Year",
                yaxis_title="Volume (Tons)",
                margin=dict(l=40, r=40, t=40, b=40),
                template="plotly_white"
            )
            st.plotly_chart(fig_year, use_container_width=True)
        else:
            st.info("Year information not available.")

    ### TAB 3: BREAKDOWN
    with tabs[2]:
        st.header("Breakdown Analysis")
        # Top 5 Partners (by Volume)
        st.subheader("Top 5 Partners")
        partner_top = df.groupby("Partner", as_index=False)["Tons"].sum().sort_values("Tons", ascending=False).head(5)
        fig_partner = px.bar(
            partner_top,
            x="Partner",
            y="Tons",
            title="Top 5 Partners by Volume",
            text_auto=True,
            color="Tons",
            color_continuous_scale="Blues"
        )
        fig_partner.update_layout(
            xaxis_title="Partner",
            yaxis_title="Volume (Tons)",
            margin=dict(l=40, r=40, t=40, b=40),
            template="plotly_white"
        )
        st.plotly_chart(fig_partner, use_container_width=True)
        
        # Additional breakdown: Volume Distribution by Flow (if available)
        if "Flow" in df.columns:
            st.subheader("Volume Distribution by Flow")
            flow_summary = df.groupby("Flow", as_index=False)["Tons"].sum()
            fig_flow = px.pie(
                flow_summary,
                names="Flow",
                values="Tons",
                title="Volume Distribution by Flow",
                hole=0.4
            )
            fig_flow.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_flow, use_container_width=True)

    ### TAB 4: DETAILED ANALYSIS
    with tabs[3]:
        st.header("Detailed Analysis")
        st.markdown("Drill down into the data for granular insights.")
        # Allow user to choose the dimension (Partner or Reporter) for analysis.
        dimension = st.radio("Select Dimension for Detailed Analysis:", ("Partner", "Reporter"), index=0)
        entities = sorted(df[dimension].dropna().unique().tolist())
        selected_entity = st.selectbox(f"Select {dimension}:", entities)
        detailed_data = df[df[dimension] == selected_entity]
        
        st.subheader(f"Trade Data for {dimension}: {selected_entity}")
        st.dataframe(detailed_data, use_container_width=True)
        
        st.markdown("##### Pivot Table: Volume by Period")
        pivot = detailed_data.pivot_table(
            index=dimension,
            columns="Period",
            values="Tons",
            aggfunc="sum",
            fill_value=0
        )
        st.dataframe(pivot)
        
        st.markdown("##### Trend Analysis")
        entity_trend = detailed_data.groupby(["Period", "Period_dt"], as_index=False)["Tons"].sum()
        if "Period_dt" in entity_trend.columns:
            entity_trend = entity_trend.sort_values("Period_dt")
        else:
            entity_trend = entity_trend.sort_values("Period")
        fig_entity = px.line(
            entity_trend,
            x="Period",
            y="Tons",
            title=f"Trade Volume Trend for {selected_entity}",
            markers=True
        )
        fig_entity.update_layout(
            xaxis=dict(title="Period", tickangle=-45),
            yaxis=dict(title="Volume (Tons)"),
            margin=dict(l=40, r=40, t=40, b=80),
            template="plotly_white"
        )
        st.plotly_chart(fig_entity, use_container_width=True)
        st.success("Detailed Analysis loaded successfully!")
    
    st.success("✅ Market Overview Dashboard loaded successfully!")
