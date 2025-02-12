# filters.py
import streamlit as st
import pandas as pd
import re
import logging
from rapidfuzz import process, fuzz

logger = logging.getLogger(__name__)

# For sorting months when provided in abbreviated form.
MONTH_ORDER = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

def dynamic_multiselect(label: str, column: str, df: pd.DataFrame):
    """
    Create a sidebar multiselect for the specified column.
    If the column is not found, display an error and return an empty list.
    For the 'Month' column, the options are sorted according to MONTH_ORDER.
    """
    if column not in df.columns:
        st.sidebar.error(f"Column '{column}' not found in data.")
        return []
    
    options = df[column].dropna().unique().tolist()
    if column == "Month":
        options = sorted(options, key=lambda m: MONTH_ORDER.get(m, 99))
    else:
        options = sorted(options)
    
    # The default is empty, meaning no filtering; if the user selects values, those will be used.
    selected = st.sidebar.multiselect(f"📌 {label}:", options, default=[], key=f"multiselect_{column}")
    return options if not selected else selected

def apply_filters(df: pd.DataFrame):
    """
    Display global filters in the sidebar and apply them to the DataFrame.
    Filters include: Year, Month, and Partner.
    
    Returns:
        filtered_df (pd.DataFrame): The DataFrame after applying filters.
        unit_column (str): The name of the unit column (e.g., "Tons").
    """
    st.sidebar.header("🔍 Global Data Filters")
    filtered_df = df.copy()
    
    # Filter by Year
    selected_years = dynamic_multiselect("Select Year", "Year", filtered_df)
    if selected_years:
        filtered_df = filtered_df[filtered_df["Year"].isin(selected_years)]
    
    # Filter by Month
    selected_months = dynamic_multiselect("Select Month", "Month", filtered_df)
    if selected_months:
        filtered_df = filtered_df[filtered_df["Month"].isin(selected_months)]
    
    # Filter by Partner
    selected_partners = dynamic_multiselect("Select Partner", "Partner", filtered_df)
    if selected_partners:
        filtered_df = filtered_df[filtered_df["Partner"].isin(selected_partners)]
    
    return filtered_df, "Tons"
