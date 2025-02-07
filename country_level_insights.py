# country_level_insights.py
import streamlit as st
import altair as alt
import pandas as pd
from filters import add_filters

def show_country_level_insights():
    st.header("Country-Level Insights")
    from core_system import df  # Global data
    df_filtered = add_filters(df)
    country_data = df_filtered.groupby("Partner", as_index=False)["Tons"].sum()
    chart = alt.Chart(country_data).mark_bar().encode(
        x=alt.X("Tons:Q", title="Total Tonnage"),
        y=alt.Y("Partner:N", sort='-x', title="Partner"),
        tooltip=["Partner", alt.Tooltip("Tons:Q", format=",.2f")]
    ).properties(width=700, height=400)
    st.altair_chart(chart, use_container_width=True)
