# detailed_analysis.py
import streamlit as st
import pandas as pd
from data_loader import upload_data
from filters import add_filters

def show_detailed_analysis():
    st.header("Detailed Analysis")
    # Use the uploaded data
    from core_system import df  # Or pass df as an argument
    df_filtered = add_filters(df)
    st.dataframe(df_filtered.sort_values("Date", ascending=False))
