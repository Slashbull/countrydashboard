# market_overview.py
import streamlit as st
import altair as alt
from filters import add_filters
from calculations import calculate_kpis

def show_market_overview():
    st.header("Market Overview")
    df = st.session_state.get("uploaded_data")
    if df is None or df.empty:
        st.warning("No data available.")
        return
    df_filtered = add_filters(df)
    kpis = calculate_kpis(df_filtered)
    col1, col2 = st.columns(2)
    col1.metric("Total Tonnage", f"{kpis['total_tons']:.2f}")
    col2.metric("Average Monthly", f"{kpis['avg_monthly']:.2f}")
    
    chart = alt.Chart(df_filtered).mark_line(point=True).encode(
        x='Date:T',
        y='sum(Tons):Q',
        tooltip=['Date:T', alt.Tooltip('sum(Tons):Q', title="Tonnage", format=",.2f")]
    ).properties(width=700, height=400).interactive()
    st.altair_chart(chart, use_container_width=True)
