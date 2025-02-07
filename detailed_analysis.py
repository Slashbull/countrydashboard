# detailed_analysis.py
import streamlit as st
from filters import add_filters

def show_detailed_analysis():
    st.header("Detailed Analysis")
    from core_system import data  # Global data
    df_filtered = add_filters(data)
    st.dataframe(df_filtered.sort_values("Date", ascending=False))
