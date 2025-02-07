# country_level_insights.py
import streamlit as st
import pandas as pd
import altair as alt
from data_loader import load_data
from filters import add_filters

def show_country_level_insights():
    st.header("Country-Level Insights")
    df = load_data()
    df = add_filters(df)
    # Group by Partner (assuming partner represents countries)
    country_data = df.groupby("Partner", as_index=False)["Tons"].sum()
    bar_chart = alt.Chart(country_data).mark_bar().encode(
        x=alt.X("Tons:Q", title="Total Tonnage"),
        y=alt.Y("Partner:N", sort='-x', title="Country"),
        tooltip=["Partner", alt.Tooltip("Tons:Q", format=",.2f")]
    ).properties(width=700, height=400)
    st.altair_chart(bar_chart, use_container_width=True)
