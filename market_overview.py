# market_overview.py
import streamlit as st
import altair as alt
import pandas as pd
from filters import add_filters

def show_market_overview():
    st.header("Market Overview")
    from core_system import data  # Global data loaded in core_system.py
    df_filtered = add_filters(data)
    
    # Inline KPI calculations here (no separate module)
    total_tons = df_filtered["Tons"].sum() if "Tons" in df_filtered.columns else 0
    if "Date" in df_filtered.columns:
        monthly = df_filtered.groupby(pd.Grouper(key="Date", freq="M"))["Tons"].sum()
        avg_monthly = monthly.mean()
    else:
        avg_monthly = 0

    col1, col2 = st.columns(2)
    col1.metric("Total Tonnage", f"{total_tons:.2f}")
    col2.metric("Average Monthly", f"{avg_monthly:.2f}")
    
    chart = alt.Chart(df_filtered).mark_line(point=True).encode(
        x='Date:T',
        y=alt.Y('sum(Tons):Q', title="Tonnage"),
        tooltip=['Date:T', alt.Tooltip('sum(Tons):Q', title="Tonnage", format=",.2f")]
    ).properties(width=700, height=400).interactive()
    st.altair_chart(chart, use_container_width=True)
