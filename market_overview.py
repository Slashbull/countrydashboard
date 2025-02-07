# market_overview.py
import streamlit as st
import altair as alt
from data_loader import upload_data
from filters import add_filters
from calculations import calculate_kpis

def show_market_overview():
    st.header("Market Overview")
    # Assume the data is already loaded and stored in session_state via core_system.py
    # Here we use the global DataFrame.
    from core_system import df  # Alternatively, pass df as an argument
    # For demonstration, we load data again (if needed):
    # df = upload_data()
    df = add_filters(df)
    kpis = calculate_kpis(df)
    col1, col2 = st.columns(2)
    col1.metric("Total Tonnage", f"{kpis['total_tons']:.2f}")
    col2.metric("Average Monthly", f"{kpis['avg_monthly']:.2f}")
    
    # Time Series Chart
    chart = alt.Chart(df).mark_line(point=True).encode(
        x='Date:T',
        y='sum(Tons):Q',
        tooltip=['Date:T', alt.Tooltip('sum(Tons):Q', title="Tonnage", format=",.2f")]
    ).properties(width=700, height=400).interactive()
    st.altair_chart(chart, use_container_width=True)
