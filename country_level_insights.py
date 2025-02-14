# country_level_insights.py
import streamlit as st
import pandas as pd
import plotly.express as px

def country_level_insights_dashboard(data: pd.DataFrame):
    st.title("🌍 Partner-Based Country-Level Insights")
    st.markdown("""
    This dashboard provides insights on trade volume aggregated by trade partners.  
    Explore trade performance, market share, and trends over time by partner.
    """)

    # Validate required columns.
    required_cols = ["Partner", "Tons"]
    missing = [col for col in required_cols if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing required columns: {', '.join(missing)}")
        return

    # Ensure 'Tons' is numeric.
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")

    # Group data by Partner.
    partner_data = data.groupby("Partner", as_index=False)["Tons"].sum()
    partner_data = partner_data.sort_values("Tons", ascending=False)
    total_volume = partner_data["Tons"].sum()

    st.markdown("### Trade Volume by Partner")
    st.dataframe(partner_data)

    # Bar Chart: Trade Volume by Partner.
    fig_bar = px.bar(
        partner_data,
        x="Partner",
        y="Tons",
        title="Trade Volume by Partner",
        labels={"Tons": "Volume (Tons)"},
        text_auto=True,
        template="plotly_white"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Donut Chart: Market Share by Partner.
    st.markdown("### Market Share by Partner")
    partner_data["Share (%)"] = (partner_data["Tons"] / total_volume) * 100
    fig_donut = px.pie(
        partner_data,
        names="Partner",
        values="Tons",
        title="Market Share by Partner",
        hole=0.4,
        hover_data={"Share (%)":":.2f"},
        template="plotly_white"
    )
    st.plotly_chart(fig_donut, use_container_width=True)

    # Trend Analysis: If 'Period' exists, allow time-series view for a selected partner.
    if "Period" in data.columns:
        st.markdown("### Partner Trend Analysis")
        selected_partner = st.selectbox("Select a Partner for Trend Analysis:", partner_data["Partner"].unique())
        partner_trend = data[data["Partner"] == selected_partner].groupby("Period")["Tons"].sum().reset_index()
        partner_trend = partner_trend.sort_values("Period")
        if not partner_trend.empty:
            fig_trend = px.line(
                partner_trend,
                x="Period",
                y="Tons",
                title=f"Trade Volume Trend for {selected_partner}",
                markers=True,
                template="plotly_white"
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No time series data available for the selected partner.")

    # OPTIONAL: Choropleth Map (if ISO mapping available)
    st.markdown("### Geographic Distribution (Choropleth)")
    # Sample ISO mapping (extend this dictionary as needed)
    iso_mapping = {
        "PartnerA": "USA",
        "PartnerB": "CHN",
        "PartnerC": "DEU",
        "PartnerD": "IND",
        "PartnerE": "BRA"
        # Add more partner-country mappings here...
    }
    partner_data["iso_alpha"] = partner_data["Partner"].map(iso_mapping)
    if partner_data["iso_alpha"].isnull().all():
        st.info("No geographic mapping available. Please update the ISO mapping.")
    else:
        fig_map = px.choropleth(
            partner_data.dropna(subset=["iso_alpha"]),
            locations="iso_alpha",
            color="Tons",
            hover_name="Partner",
            color_continuous_scale=px.colors.sequential.Plasma,
            title="Trade Volume by Partner (Geographic View)"
        )
        st.plotly_chart(fig_map, use_container_width=True)
    
    # Download option for partner data.
    csv_data = partner_data.to_csv(index=False).encode("utf-8")
    st.download_button("Download Partner Data as CSV", csv_data, "partner_data.csv", "text/csv")
    
    st.success("✅ Partner-Based Insights loaded successfully!")
