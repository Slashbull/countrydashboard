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
    
    # Use filtered data if available (set in st.session_state by your filters module), otherwise use raw data.
    df = st.session_state.get("filtered_data", data).copy()
    
    # --- Create the 'Period' column if not already present ---
    if "Period" not in df.columns:
        try:
            def parse_period(row):
                month_val = row["Month"]
                year_val = str(row["Year"])
                # If Month is numeric (e.g. 1), parse as month number; otherwise, assume abbreviated text.
                if str(month_val).isdigit():
                    return datetime.strptime(f"{int(month_val)} {year_val}", "%m %Y")
                else:
                    return datetime.strptime(f"{month_val} {year_val}", "%b %Y")
            df["Period_dt"] = df.apply(parse_period, axis=1)
            sorted_periods = sorted(df["Period_dt"].dropna().unique())
            period_labels = [dt.strftime("%b-%Y") for dt in sorted_periods]
            df["Period"] = df["Period_dt"].dt.strftime("%b-%Y")
            df["Period"] = pd.Categorical(df["Period"], categories=period_labels, ordered=True)
        except Exception as e:
            st.error("Error creating 'Period' column. Please check the Month and Year formats.")
            st.error(e)
            return

    # --- Dashboard Layout with Tabs ---
    tabs = st.tabs(["Summary", "Trends", "Breakdown", "Detailed Analysis"])

    ### Tab 1: Summary
    with tabs[0]:
        st.header("Key Performance Indicators")
        total_volume = df["Tons"].sum()
        unique_partners = df["Partner"].nunique()
        unique_reporters = df["Reporter"].nunique()
        avg_volume = total_volume / unique_partners if unique_partners > 0 else 0

        # Calculate Month-over-Month (MoM) growth
        periods_sorted = df.sort_values("Period_dt")["Period"].unique() if "Period_dt" in df.columns else df["Period"].unique()
        if len(periods_sorted) >= 2:
            last_period = periods_sorted[-1]
            second_last_period = periods_sorted[-2]
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
        total_partner_volume = partner_summary["Tons"].sum()
        partner_summary["Percentage"] = (partner_summary["Tons"] / total_partner_volume) * 100
        fig_donut = px.pie(
            partner_summary, 
            names="Partner", 
            values="Tons", 
            title="Market Share by Partner", 
            hole=0.4,
            hover_data={"Percentage":":.2f"}
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    ### Tab 2: Trends
    with tabs[1]:
        st.header("Monthly & Yearly Trends")
        # --- Overall Monthly Trend ---
        monthly_trends = df.groupby(["Period", "Period_dt"], as_index=False)["Tons"].sum().sort_values("Period_dt")
        fig_overall = px.line(
            monthly_trends,
            x="Period",
            y="Tons",
            title="Overall Monthly Trade Volume Trend",
            markers=True
        )
        fig_overall.update_layout(
            xaxis=dict(title="Period", tickangle=-45),
            yaxis=dict(title="Volume (Tons)"),
            margin=dict(l=40, r=40, t=40, b=80),
            template="plotly_white"
        )
        st.plotly_chart(fig_overall, use_container_width=True)
        
        st.markdown("---")
        
        # --- Monthly Trend by Year ---
        if "Year" in df.columns and "Month" in df.columns:
            # Convert Month to abbreviated string if necessary.
            df["Month_str"] = df["Month"].apply(
                lambda x: datetime.strptime(str(x), "%m").strftime("%b") if str(x).isdigit() else x
            )
            month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            df["Month_str"] = pd.Categorical(df["Month_str"], categories=month_order, ordered=True)
            monthly_by_year = df.groupby(["Year", "Month_str"], as_index=False)["Tons"].sum().sort_values(["Year", "Month_str"])
            fig_by_year = px.line(
                monthly_by_year,
                x="Month_str",
                y="Tons",
                color="Year",
                title="Monthly Trend by Year",
                markers=True
            )
            fig_by_year.update_layout(
                xaxis=dict(title="Month"),
                yaxis=dict(title="Volume (Tons)"),
                margin=dict(l=40, r=40, t=40, b=40),
                template="plotly_white"
            )
            st.plotly_chart(fig_by_year, use_container_width=True)
        else:
            st.info("Year and/or Month information not available for monthly trend by year.")
        
        st.markdown("---")
        
        # --- Yearly Trend (Optional) ---
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

    ### Tab 3: Breakdown
    with tabs[2]:
        st.header("Breakdown Analysis")
        st.subheader("Top 5 Partners")
        partner_top = (df.groupby("Partner", as_index=False)["Tons"]
                       .sum().sort_values("Tons", ascending=False).head(5))
        fig_partner = px.bar(
            partner_top,
            x="Partner",
            y="Tons",
            title="Top 5 Partners by Volume",
            text_auto=True
        )
        st.plotly_chart(fig_partner, use_container_width=True)
        
        st.subheader("Volume Distribution by Flow")
        if "Flow" in df.columns:
            flow_summary = df.groupby("Flow", as_index=False)["Tons"].sum()
            fig_flow = px.pie(
                flow_summary,
                names="Flow",
                values="Tons",
                title="Volume Distribution by Flow",
                hole=0.4
            )
            st.plotly_chart(fig_flow, use_container_width=True)
        else:
            st.info("Flow information not available.")

    ### Tab 4: Detailed Analysis
    with tabs[3]:
        st.header("Detailed Analysis")
        st.markdown("Drill down into the data for granular insights.")
        # Let the user choose the dimension for detailed analysis.
        dimension = st.radio("Select Dimension for Detailed Analysis:", ("Partner", "Reporter"), index=0)
        entities = sorted(df[dimension].dropna().unique().tolist())
        selected_entity = st.selectbox(f"Select {dimension}:", entities)
        detailed_data = df[df[dimension] == selected_entity]
        st.subheader(f"Trade Data for {dimension}: {selected_entity}")
        st.dataframe(detailed_data)
        
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
        entity_trend = detailed_data.groupby("Period", as_index=False)["Tons"].sum()
        if "Period_dt" in detailed_data.columns:
            period_map = detailed_data.drop_duplicates("Period")[["Period", "Period_dt"]]
            entity_trend = pd.merge(entity_trend, period_map, on="Period", how="left")
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
        st.plotly_chart(fig_entity, use_container_width=True)
        st.success("Detailed Analysis loaded successfully!")
    
    st.success("✅ Market Overview Dashboard loaded successfully!")
