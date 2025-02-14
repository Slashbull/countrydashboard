# market_overview.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def market_overview_dashboard(data: pd.DataFrame):
    st.title("📊 Market Overview Dashboard")
    
    # --- Validate Required Columns ---
    required_columns = ["SR NO.", "Year", "Month", "Reporter", "Flow", "Partner", "Code", "Desc", "Tons"]
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing columns: {', '.join(missing)}")
        return
    
    # --- Ensure 'Tons' is Numeric ---
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")
    
    # Work on a copy of the data
    df = data.copy()
    
    # --- Create 'Period' Column if Not Present ---
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
            st.error("Error creating 'Period' column. Check Month and Year formats.")
            st.error(e)
            return

    # --- Calculate Key Performance Indicators (KPIs) ---
    total_volume = df["Tons"].sum()
    total_records = df.shape[0]
    unique_partners = df["Partner"].nunique()
    unique_reporters = df["Reporter"].nunique()
    avg_volume_partner = total_volume / unique_partners if unique_partners > 0 else 0

    # Month-over-Month (MoM) Growth
    periods = list(df["Period"].cat.categories)
    if len(periods) >= 2:
        last_period = periods[-1]
        second_last_period = periods[-2]
        vol_last = df[df["Period"] == last_period]["Tons"].sum()
        vol_prev = df[df["Period"] == second_last_period]["Tons"].sum()
        mom_growth = ((vol_last - vol_prev) / vol_prev * 100) if vol_prev != 0 else 0
    else:
        mom_growth = 0

    # Year-over-Year (YoY) Growth if multiple years exist
    if df["Year"].nunique() > 1:
        yearly_vol = df.groupby("Year")["Tons"].sum().reset_index().sort_values("Year")
        if len(yearly_vol) >= 2:
            current_year = yearly_vol.iloc[-1]["Tons"]
            previous_year = yearly_vol.iloc[-2]["Tons"]
            yoy_growth = ((current_year - previous_year) / previous_year * 100) if previous_year != 0 else 0
        else:
            yoy_growth = 0
    else:
        yoy_growth = None

    # Top Partner & Partner Concentration
    partner_vol = df.groupby("Partner")["Tons"].sum().reset_index().sort_values("Tons", ascending=False)
    if not partner_vol.empty:
        top_partner = partner_vol.iloc[0]["Partner"]
        top_partner_volume = partner_vol.iloc[0]["Tons"]
        top_partner_share = (top_partner_volume / total_volume * 100) if total_volume > 0 else 0
        top_3_volume = partner_vol.head(3)["Tons"].sum()
        concentration_ratio = (top_3_volume / total_volume * 100) if total_volume > 0 else 0
    else:
        top_partner, top_partner_share, concentration_ratio = "N/A", 0, 0

    # --- Create Dashboard Tabs ---
    tabs = st.tabs(["Summary", "Trends", "Growth", "Breakdown", "Detailed Analysis"])

    ## Tab 1: Summary
    with tabs[0]:
        st.header("Summary Metrics")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Volume (Tons)", f"{total_volume:,.2f}")
        col1.metric("Total Records", total_records)
        col2.metric("Unique Partners", unique_partners)
        col2.metric("Unique Reporters", unique_reporters)
        col3.metric("Avg Volume/Partner", f"{avg_volume_partner:,.2f}")
        col3.metric("MoM Growth (%)", f"{mom_growth:,.2f}")
        if yoy_growth is not None:
            st.metric("YoY Growth (%)", f"{yoy_growth:,.2f}")
        st.markdown("---")
        st.subheader("Top Partner & Concentration")
        st.write(f"**Top Partner:** {top_partner} ({top_partner_share:,.2f}% of total volume)")
        st.write(f"**Top 3 Partner Concentration:** {concentration_ratio:,.2f}% of total volume")
        st.markdown("---")
        st.subheader("Market Share by Partner")
        partner_summary = partner_vol.copy()
        partner_summary["Share (%)"] = (partner_summary["Tons"] / total_volume) * 100
        fig_donut = px.pie(
            partner_summary,
            names="Partner",
            values="Tons",
            title="Market Share by Partner",
            hole=0.4,
            hover_data={"Share (%)":":.2f"},
            template="plotly_white"
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        if "Period_dt" in df.columns:
            last_updated = df["Period_dt"].max().strftime("%b-%Y")
            st.info(f"Data last updated: {last_updated}")

    ## Tab 2: Trends
    with tabs[1]:
        st.header("Trends Analysis")
        st.subheader("Overall Monthly Trends")
        monthly_trends = df.groupby("Period")["Tons"].sum().reset_index().sort_values("Period")
        fig_line = px.line(
            monthly_trends,
            x="Period",
            y="Tons",
            title="Monthly Trade Volume Trends",
            markers=True,
            template="plotly_white"
        )
        fig_line.update_layout(xaxis_title="Period", yaxis_title="Volume (Tons)")
        st.plotly_chart(fig_line, use_container_width=True)
        st.markdown("---")
        if df["Year"].nunique() > 1:
            st.subheader("Monthly Trends by Year")
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
            fig_year = px.line(
                yearly_trends,
                x="Month",
                y="Tons",
                color="Year",
                title="Monthly Trends by Year",
                markers=True,
                template="plotly_white"
            )
            fig_year.update_layout(xaxis_title="Month", yaxis_title="Volume (Tons)")
            st.plotly_chart(fig_year, use_container_width=True)
        else:
            st.info("Not enough year data for year-wise trends.")

    ## Tab 3: Growth
    with tabs[2]:
        st.header("Growth Analysis")
        st.subheader("Monthly Growth (%)")
        monthly_growth = []
        periods = list(df["Period"].cat.categories)
        for i in range(1, len(periods)):
            vol_current = df[df["Period"] == periods[i]]["Tons"].sum()
            vol_previous = df[df["Period"] == periods[i-1]]["Tons"].sum()
            growth = ((vol_current - vol_previous) / vol_previous * 100) if vol_previous != 0 else 0
            monthly_growth.append({"Period": periods[i], "Growth (%)": growth})
        df_growth = pd.DataFrame(monthly_growth)
        fig_growth = px.bar(
            df_growth,
            x="Period",
            y="Growth (%)",
            title="Month-over-Month Growth (%)",
            text_auto=True,
            template="plotly_white"
        )
        st.plotly_chart(fig_growth, use_container_width=True)
        st.markdown("---")
        st.subheader("Yearly Growth (%)")
        if df["Year"].nunique() > 1:
            yearly_vol = df.groupby("Year")["Tons"].sum().reset_index().sort_values("Year")
            yearly_growth = []
            years = yearly_vol["Year"].tolist()
            for i in range(1, len(years)):
                current = yearly_vol[yearly_vol["Year"] == years[i]]["Tons"].values[0]
                previous = yearly_vol[yearly_vol["Year"] == years[i-1]]["Tons"].values[0]
                growth = ((current - previous) / previous * 100) if previous != 0 else 0
                yearly_growth.append({"Year": years[i], "Growth (%)": growth})
            df_yearly_growth = pd.DataFrame(yearly_growth)
            fig_yoy = px.bar(
                df_yearly_growth,
                x="Year",
                y="Growth (%)",
                title="Year-over-Year Growth (%)",
                text_auto=True,
                template="plotly_white",
                color="Growth (%)",
                color_continuous_scale="RdYlGn"
            )
            st.plotly_chart(fig_yoy, use_container_width=True)
        else:
            st.info("Not enough year data to compute YoY growth.")
        
        # New: Yearly Trade Volume Chart by Month
        st.markdown("---")
        st.subheader("Yearly Trade Volume Breakdown by Month")
        if df["Year"].nunique() > 1:
            # Create a pivot table: rows=Year, columns=Month (as abbreviated)
            yearly_monthly = df.pivot_table(index="Year", columns="Month", values="Tons", aggfunc="sum", fill_value=0)
            # Sort columns by month order (if numeric months are present)
            try:
                yearly_monthly = yearly_monthly.reindex(columns=sorted(yearly_monthly.columns, key=lambda m: int(m) if str(m).isdigit() else m))
            except:
                # If not numeric, assume already in order.
                pass
            fig_yearly_monthly = px.imshow(
                yearly_monthly,
                labels=dict(x="Month", y="Year", color="Volume (Tons)"),
                x=yearly_monthly.columns,
                y=yearly_monthly.index,
                title="Yearly Trade Volume Breakdown by Month",
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig_yearly_monthly, use_container_width=True)
        else:
            st.info("Not enough year data for yearly breakdown.")

    ## Tab 4: Breakdown
    with tabs[3]:
        st.header("Breakdown Analysis")
        st.subheader("Top 5 Partners")
        top5 = partner_vol.head(5)
        fig_top5 = px.bar(
            top5,
            x="Partner",
            y="Tons",
            title="Top 5 Partners by Volume",
            text_auto=True,
            template="plotly_white"
        )
        st.plotly_chart(fig_top5, use_container_width=True)
        st.markdown("---")
        st.subheader("Volume Distribution by Flow")
        if "Flow" in df.columns:
            flow_summary = df.groupby("Flow", as_index=False)["Tons"].sum()
            fig_flow = px.pie(
                flow_summary,
                names="Flow",
                values="Tons",
                title="Volume Distribution by Flow",
                hole=0.4,
                template="plotly_white"
            )
            st.plotly_chart(fig_flow, use_container_width=True)
        else:
            st.info("Flow information not available.")
    
    ## Tab 5: Detailed Analysis
    with tabs[4]:
        st.header("Detailed Analysis")
        st.markdown("Drill down into the data for granular insights.")
        dimension = st.radio("Select Dimension for Detailed Analysis:", ("Partner", "Reporter"), index=0)
        entities = sorted(df[dimension].dropna().unique().tolist())
        selected_entity = st.selectbox(f"Select {dimension}:", entities)
        detail_data = df[df[dimension] == selected_entity]
        st.subheader(f"Trade Data for {dimension}: {selected_entity}")
        st.dataframe(detail_data)
        st.markdown("##### Pivot Table: Volume by Period")
        pivot = detail_data.pivot_table(
            index=dimension,
            columns="Period",
            values="Tons",
            aggfunc="sum",
            fill_value=0
        )
        st.dataframe(pivot)
        st.markdown("##### Trend Analysis")
        entity_trend = detail_data.groupby("Period", as_index=False)["Tons"].sum()
        if "Period_dt" in detail_data.columns:
            period_map = detail_data.drop_duplicates("Period")[["Period", "Period_dt"]]
            entity_trend = pd.merge(entity_trend, period_map, on="Period", how="left")
            entity_trend = entity_trend.sort_values("Period_dt")
        else:
            entity_trend = entity_trend.sort_values("Period")
        fig_entity = px.line(
            entity_trend,
            x="Period",
            y="Tons",
            title=f"Trade Volume Trend for {selected_entity}",
            markers=True,
            template="plotly_white"
        )
        st.plotly_chart(fig_entity, use_container_width=True)
        st.success("Detailed Analysis loaded successfully!")
    
    st.success("✅ Market Overview Dashboard loaded successfully!")
