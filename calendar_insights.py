# calendar_insights.py
import streamlit as st
import pandas as pd
import altair as alt
from data_loader import load_data
from filters import add_filters

def show_calendar_insights():
    st.header("Calendar/Business Cycle Insights")
    df = load_data()
    df = add_filters(df)
    # Create a simple pivot table: Average tonnage per Month for each Year
    pivot = df.pivot_table(index="Month", columns="Year", values="Tons", aggfunc="mean")
    st.write("Average Monthly Tonnage by Year")
    st.dataframe(pivot)
    
    # Create a heatmap-like chart using Altair
    df_heat = df.copy()
    df_heat['Month_Str'] = df_heat['Month'].astype(str)
    heat = alt.Chart(df_heat).mark_rect().encode(
        x=alt.X("Year:N", title="Year"),
        y=alt.Y("Month_Str:N", title="Month"),
        color=alt.Color("mean(Tons):Q", title="Avg Tonnage"),
        tooltip=[alt.Tooltip("mean(Tons):Q", format=",.2f")]
    ).properties(width=700, height=400)
    st.altair_chart(heat, use_container_width=True)
