# filters.py
import streamlit as st
import pandas as pd

def add_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filter Data")
    # Example filters (adjust according to your actual column names)
    years = df['Year'].unique().tolist()
    selected_years = st.sidebar.multiselect("Select Year(s)", options=years, default=years)
    
    months = df['Month'].unique().tolist()
    selected_months = st.sidebar.multiselect("Select Month(s)", options=months, default=months)
    
    reporters = df['Reporter'].unique().tolist()
    selected_reporters = st.sidebar.multiselect("Select Reporter(s)", options=reporters, default=reporters)
    
    partners = df['Partner'].unique().tolist()
    selected_partners = st.sidebar.multiselect("Select Partner(s)", options=partners, default=partners)
    
    codes = df['Code'].unique().tolist()
    selected_codes = st.sidebar.multiselect("Select Code(s)", options=codes, default=codes)
    
    filtered_df = df[
        (df['Year'].isin(selected_years)) &
        (df['Month'].isin(selected_months)) &
        (df['Reporter'].isin(selected_reporters)) &
        (df['Partner'].isin(selected_partners)) &
        (df['Code'].isin(selected_codes))
    ]
    return filtered_df
