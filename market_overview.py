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

    # Convert the 'Tons' column to numeric.
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    
    # Work on a copy of the data.
    df = data.copy()
    
    # --- Create the 'Period' column if not present ---
    if "Period" not in df.columns:
        try:
            def parse_period(row):
                m = row["Month"]
                y = str(row["Year"])
                if str(m).isdigit():
                    return datetime.strptime(f"{int(m)} {y}", "%m %Y")
                else:
                    return datetime.strptime(f"{m} {y}", "%b %Y")
            df["Period_dt"] = df.apply(parse_period, axis=1)
            sorted_periods = sorted(df["Period_dt"].dropna().unique())
            period_labels = [dt.strftime("%b-%Y") for dt in sorted_periods]
            df["Period"] = df["Period_dt"].dt.strftime("%b-%Y")
            df["Period"] = pd.Categorical(df["Period"], categories=period_labels, ordered=True)
        except Exception as e:
            st.error("Error creating 'Period' column. Please check Month and Year formats.")
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

        # Calculate Month-over-Month (MoM) Growth
        if "Period_dt" in df.columns:
            periods_sorted = df.sort_values("Period_dt")["Period"].unique()
        else:
            periods_sorted = df["Period"].unique()
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
        st.subheader("Overall Monthly Trends")
        monthly_trends = df.groupby("Period")["Tons"].sum().reset_index()
        monthly_trends["Period_str"] = monthly_trends["Period"].astype(str)
        fig_line = px.line(
            monthly_trends, 
            x="Period_str", 
            y="Tons",
            title="Monthly Import Trends", 
            markers=True
        )
        fig_line.update_layout(
            xaxis_title="Period",
            yaxis_title="Volume (Tons)",
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig_line, use_container_width=True)
        
        st.markdown("---")
        if df["Year"].nunique() > 1:
            st.markdown("#### Trends by Year")
            yearly_trends = df.groupby(["Year", "Month"])["Tons"].sum().reset_index()
            def convert_month(m):
                try:
                    m_int = int(m)
                    return datetime.strptime(str(m_int), "%m").strftime("%b")
                except:
                    return m
            yearly_trends["Month"] = yearly_trends["Month"].apply(convert_month)
            month_order = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
                           "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
            yearly_trends["Month_Order"] = yearly_trends["Month"].map(month_order)
            yearly_trends = yearly_trends.sort_values("Month_Order")
            fig_yearly = px.line(
                yearly_trends,
                x="Month",
                y="Tons",
                color="Year",
                title="Monthly Trends by Year",
                markers=True
            )
            st.plotly_chart(fig_yearly, use_container_width=True)
        else:
            st.info("Not enough year information for Trends by Year.")

        st.markdown("---")
        if "Year" in df.columns:
            st.subheader("Yearly Trade Volume")
            yearly_total = df.groupby("Year", as_index=False)["Tons"].sum().sort_values("Year")
            fig_year = px.bar(
                yearly_total,
                x="Year",
                y="Tons",
                title="Yearly Trade Volume",
                text_auto=True
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
