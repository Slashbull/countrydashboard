# detailed_analysis.py
import streamlit as st
import pandas as pd
from data_loader import load_data
from filters import add_filters

def show_detailed_analysis():
    st.header("Detailed Analysis")
    df = load_data()
    df = add_filters(df)
    st.dataframe(df.sort_values("Date", ascending=False))
