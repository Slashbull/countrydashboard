# detailed_analysis.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def detailed_analysis_dashboard(data: pd.DataFrame):
    st.title("🔍 Detailed Analysis")

    # Validate required columns.
    required_cols = ["Reporter", "Partner", "Tons", "Year", "Month", "Period"]
    missing = [col for col in required_cols if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing required columns: {', '.join(missing)}")
        return

    # Ensure Tons is numeric.
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")

    # Create three main tabs.
    tabs = st.tabs(["Summary", "Partners Breakdown & Trends", "Detailed Partner Analysis"])

    #########################################################
    # Tab 1: Summary - Overall KPIs and Growth Metrics
    #########################################################
    with tabs[0]:
        st.header("Overall Summary")

        total_volume = data["Tons"].sum()
        total_records = data.shape[0]
        avg_volume_record = total_volume / total_records if total_records > 0 else 0

        unique_partners = data["Partner"].nunique()
        avg_volume_partner = total_volume / unique_partners if unique_partners > 0 else 0

        # Calculate Month-over-Month (MoM) Growth
        # We assume data is sorted by a proper Period; use the "Period_dt" if available.
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

        # Identify the top partner by volume.
        partner_summary = data.groupby("Partner", as_index=False)["Tons"].sum()
        partner_summary = partner_summary.sort_values("Tons", ascending=False)
        if not partner_summary.empty:
            top_partner = partner_summary.iloc[0]["Partner"]
            top_partner_volume = partner_summary.iloc[0]["Tons"]
            top_partner_share = (top_partner_volume / total_volume * 100) if total_volume > 0 else 0
        else:
            top_partner, top_partner_share = "N/A", 0

        # Display metrics in columns.
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("Total Volume (Tons)", f"{total_volume:,.2f}")
        col2.metric("Total Records", total_records)
        col3.metric("Avg Volume/Record", f"{avg_volume_record:,.2f}")
        col4.metric("Unique Partners", unique_partners)
        col5.metric("Avg Volume/Partner", f"{avg_volume_partner:,.2f}")
        col6.metric("MoM Growth (%)", f"{mom_growth:,.2f}")

        st.markdown("---")
        st.subheader("Top Partner")
        st.write(f"**{top_partner}** contributes **{top_partner_share:,.2f}%** of total volume.")

    #########################################################
    # Tab 2: Partners Breakdown & Trends
    #########################################################
    with tabs[1]:
        st.header("Partners Breakdown & Trends")

        # --- Breakdown by Partner ---
        st.subheader("Volume by Partner")
        partner_breakdown = data.groupby("Partner", as_index=False)["Tons"].sum()
        partner_breakdown = partner_breakdown.sort_values("Tons", ascending=False)
        fig_bar = px.bar(
            partner_breakdown,
            x="Partner",
            y="Tons",
            title="Volume by Partner",
            text_auto=True,
            template="plotly_white"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        # --- Donut Chart for Market Share ---
        st.subheader("Market Share by Partner")
        total_partner_volume = partner_breakdown["Tons"].sum()
        partner_breakdown["Share (%)"] = (partner_breakdown["Tons"] / total_partner_volume) * 100
        fig_donut = px.pie(
            partner_breakdown,
            names="Partner",
            values="Tons",
            title="Market Share by Partner",
            hole=0.4,
            hover_data={"Share (%)":":.2f"},
            template="plotly_white"
        )
        st.plotly_chart(fig_donut, use_container_width=True)

        st.markdown("---")
        # --- Growth Analysis: Compute recent period growth per partner ---
        st.subheader("Recent Growth by Partner")
        # Ensure there are at least two periods.
        if len(data["Period"].unique()) >= 2:
            # Get the latest period
            latest = data["Period"].unique()[-1]
            previous = data["Period"].unique()[-2]
            # Compute volume change per partner between the two periods.
            vol_latest = data[data["Period"] == latest].groupby("Partner")["Tons"].sum()
            vol_previous = data[data["Period"] == previous].groupby("Partner")["Tons"].sum()
            growth = ((vol_latest - vol_previous) / vol_previous * 100).replace([float('inf'), -float('inf')], 0)
            growth_df = growth.reset_index().rename(columns={0: "Growth (%)"})
            growth_df.columns = ["Partner", "Growth (%)"]
            growth_df["Growth (%)"] = growth_df["Growth (%)"].round(2)
            growth_df = growth_df.sort_values("Growth (%)", ascending=False)
            st.dataframe(growth_df)
            fig_growth = px.bar(
                growth_df,
                x="Partner",
                y="Growth (%)",
                title="Recent Month-over-Month Growth by Partner",
                text_auto=True,
                template="plotly_white",
                color="Growth (%)",
                color_continuous_scale="RdYlGn"
            )
            st.plotly_chart(fig_growth, use_container_width=True)
        else:
            st.info("Not enough period data to compute growth metrics.")

    #########################################################
    # Tab 3: Detailed Partner Analysis (Monthly & Yearly)
    #########################################################
    with tabs[2]:
        st.header("Detailed Partner Analysis")
        st.markdown("Drill down into a specific partner for granular insights.")
        
        # Let user choose a partner.
        partners = sorted(data["Partner"].dropna().unique().tolist())
        selected_partner = st.selectbox("Select a Partner:", partners)
        partner_data = data[data["Partner"] == selected_partner]
        st.subheader(f"Trade Data for Partner: {selected_partner}")
        st.dataframe(partner_data)

        # Pivot Table: Monthly Analysis
        st.markdown("##### Monthly Analysis")
        try:
            monthly_pivot = pd.pivot_table(
                partner_data,
                values="Tons",
                index="Period",
                aggfunc="sum",
                fill_value=0
            )
            st.dataframe(monthly_pivot)
        except Exception as e:
            st.error("Error generating monthly pivot table.")
            st.error(e)
        
        # Trend Chart: Monthly Volume Trend for the selected partner.
        st.markdown("##### Monthly Trend")
        monthly_trend = partner_data.groupby("Period", as_index=False)["Tons"].sum()
        monthly_trend = monthly_trend.sort_values("Period")
        fig_partner_trend = px.line(
            monthly_trend,
            x="Period",
            y="Tons",
            title=f"Monthly Trade Volume Trend for {selected_partner}",
            markers=True,
            template="plotly_white"
        )
        st.plotly_chart(fig_partner_trend, use_container_width=True)

        # Yearly Analysis (if Year column is available)
        if "Year" in partner_data.columns:
            st.markdown("##### Yearly Analysis")
            try:
                yearly_pivot = pd.pivot_table(
                    partner_data,
                    values="Tons",
                    index="Year",
                    aggfunc="sum",
                    fill_value=0
                )
                st.dataframe(yearly_pivot)
                fig_yearly = px.bar(
                    yearly_pivot.reset_index(),
                    x="Year",
                    y="Tons",
                    title=f"Yearly Trade Volume for {selected_partner}",
                    text_auto=True,
                    template="plotly_white"
                )
                st.plotly_chart(fig_yearly, use_container_width=True)
            except Exception as e:
                st.error("Error generating yearly analysis.")
                st.error(e)
        else:
            st.info("Year information not available for this partner.")

        st.success("Detailed Partner Analysis loaded successfully!")

    st.success("✅ Detailed Analysis Dashboard loaded successfully!")
