# market_overview.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def market_overview_dashboard(data: pd.DataFrame):
    st.title("📊 Market Overview Dashboard")
    
    # Verify required columns
    required_columns = ["SR NO.", "Year", "Month", "Reporter", "Flow", "Partner", "Code", "Desc", "Tons"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return

    # Convert 'Tons' to numeric
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    
    # Create an ordered Period column if not already present
    if "Period" not in data.columns:
        try:
            def parse_period(row):
                # If Month is numeric, parse as month number; otherwise assume abbreviated month name.
                month_val = row["Month"]
                year_val = str(row["Year"])
                if str(month_val).isdigit():
                    return datetime.strptime(f"{int(month_val)} {year_val}", "%m %Y")
                else:
                    return datetime.strptime(f"{month_val} {year_val}", "%b %Y")
            
            data["Period_dt"] = data.apply(parse_period, axis=1)
            # Create an ordered list of period labels (e.g., "Jan-2012")
            sorted_periods = sorted(data["Period_dt"].dropna().unique())
            period_labels = [dt.strftime("%b-%Y") for dt in sorted_periods]
            data["Period"] = data["Period_dt"].dt.strftime("%b-%Y")
            data["Period"] = pd.Categorical(data["Period"], categories=period_labels, ordered=True)
        except Exception as e:
            st.error("Error creating Period column. Please check Month and Year formats.")
            return

    # Define Tabs for multi‑view analysis
    tabs = st.tabs(["Summary", "Trends", "Breakdown", "Detailed Analysis"])

    ### Tab 1: Summary
    with tabs[0]:
        st.header("Key Performance Indicators")
        total_volume = data["Tons"].sum()
        unique_partners = data["Partner"].nunique()
        unique_reporters = data["Reporter"].nunique()
        avg_volume = total_volume / unique_partners if unique_partners > 0 else 0

        # Calculate Month-over-Month (MoM) growth if there are at least two periods.
        periods = list(data["Period"].cat.categories)
        if len(periods) >= 2:
            last_period = periods[-1]
            second_last_period = periods[-2]
            vol_last = data[data["Period"] == last_period]["Tons"].sum()
            vol_prev = data[data["Period"] == second_last_period]["Tons"].sum()
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
        partner_summary = data.groupby("Partner")["Tons"].sum().reset_index()
        partner_summary["Percentage"] = partner_summary["Tons"] / partner_summary["Tons"].sum() * 100
        fig_donut = px.pie(partner_summary, names="Partner", values="Tons", 
                           title="Market Share by Partner", hole=0.4,
                           hover_data={"Percentage":":.2f"})
        st.plotly_chart(fig_donut, use_container_width=True)

    ### Tab 2: Trends
    with tabs[1]:
        st.header("Monthly Trends")
        monthly_trends = data.groupby("Period")["Tons"].sum().reset_index()
        fig_line = px.line(monthly_trends, x="Period", y="Tons", 
                           title="Monthly Trade Volume Trend", markers=True)
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown("---")
        st.subheader("Yearly Trends")
        if "Year" in data.columns:
            yearly_trends = data.groupby("Year")["Tons"].sum().reset_index()
            fig_year = px.bar(yearly_trends, x="Year", y="Tons", 
                              title="Yearly Trade Volume", text_auto=True)
            st.plotly_chart(fig_year, use_container_width=True)
        else:
            st.info("Year information not available.")

    ### Tab 3: Breakdown
    with tabs[2]:
        st.header("Breakdown Analysis")
        st.subheader("Top 5 Reporters")
        reporter_summary = (data.groupby("Reporter")["Tons"]
                              .sum().reset_index().sort_values("Tons", ascending=False)
                              .head(5))
        fig_reporter = px.bar(reporter_summary, x="Reporter", y="Tons",
                              title="Top 5 Reporters by Volume", text_auto=True)
        st.plotly_chart(fig_reporter, use_container_width=True)
        st.subheader("Top 5 Partners")
        partner_top = (data.groupby("Partner")["Tons"]
                       .sum().reset_index().sort_values("Tons", ascending=False)
                       .head(5))
        fig_partner = px.bar(partner_top, x="Partner", y="Tons",
                             title="Top 5 Partners by Volume", text_auto=True)
        st.plotly_chart(fig_partner, use_container_width=True)

    ### Tab 4: Detailed Analysis
    with tabs[3]:
        st.header("Detailed Analysis")
        st.markdown("Use the controls below to drill down into the data.")
        # Example: let the user select a Reporter to analyze
        reporters = sorted(data["Reporter"].dropna().unique().tolist())
        selected_reporter = st.selectbox("Select Reporter", reporters)
        reporter_data = data[data["Reporter"] == selected_reporter]
        st.subheader(f"Trade Data for Reporter: {selected_reporter}")
        st.dataframe(reporter_data)
        
        st.markdown("##### Pivot Table: Volume by Partner and Period")
        pivot = reporter_data.pivot_table(index="Partner", columns="Period", values="Tons", aggfunc="sum", fill_value=0)
        st.dataframe(pivot)
        
        st.markdown("##### Bar Chart: Trade Volume by Partner")
        partner_data = reporter_data.groupby("Partner")["Tons"].sum().reset_index()
        fig_bar = px.bar(partner_data, x="Partner", y="Tons", 
                         title=f"Volume for {selected_reporter} by Partner", text_auto=True)
        st.plotly_chart(fig_bar, use_container_width=True)
        
        st.success("✅ Detailed Analysis loaded successfully!")
    
    st.success("✅ Market Overview Dashboard loaded successfully!")
