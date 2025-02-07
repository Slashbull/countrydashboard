# calendar_insights.py
import streamlit as st
import altair as alt

def show_calendar_insights():
    st.header("Calendar/Business Cycle Insights")
    from core_system import data  # Global data
    from filters import add_filters
    df_filtered = add_filters(data)
    pivot = df_filtered.pivot_table(index="Month", columns="Year", values="Tons", aggfunc="mean")
    st.write("Average Monthly Tonnage by Year:")
    st.dataframe(pivot)
    df_filtered['Month_Str'] = df_filtered['Month'].astype(str)
    heat = alt.Chart(df_filtered).mark_rect().encode(
        x=alt.X("Year:N", title="Year"),
        y=alt.Y("Month_Str:N", title="Month"),
        color=alt.Color("mean(Tons):Q", title="Avg Tonnage"),
        tooltip=[alt.Tooltip("mean(Tons):Q", format=",.2f")]
    ).properties(width=700, height=400)
    st.altair_chart(heat, use_container_width=True)
