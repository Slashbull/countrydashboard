# filters.py
import streamlit as st
import pandas as pd

# Predefined order for months (when using abbreviated month names)
MONTH_ORDER = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

def dynamic_multiselect(label: str, column: str, df: pd.DataFrame):
    """Create a simple sidebar multiselect widget for a given column."""
    if column not in df.columns:
        st.sidebar.error(f"Column '{column}' not found in data.")
        return []
    options = list(df[column].dropna().unique())
    if column == "Month":
        options = sorted(options, key=lambda m: MONTH_ORDER.get(m, 99))
    else:
        options = sorted(options)
    # All filter keys start with "multiselect_"
    selected = st.sidebar.multiselect(f"{label}:", options, default=[], key=f"multiselect_{column}")
    # If nothing is selected, return all options (i.e. no filtering)
    return options if not selected else selected

def apply_filters(df: pd.DataFrame):
    """
    Display global filters (Year, Month, and Partner) in the sidebar and apply them.
    Returns the filtered DataFrame and the unit column ("Tons").
    """
    st.sidebar.header("Global Filters")
    filtered_df = df.copy()
    
    years = dynamic_multiselect("Select Year", "Year", filtered_df)
    if years:
        filtered_df = filtered_df[filtered_df["Year"].isin(years)]
    
    months = dynamic_multiselect("Select Month", "Month", filtered_df)
    if months:
        filtered_df = filtered_df[filtered_df["Month"].isin(months)]
    
    partners = dynamic_multiselect("Select Partner", "Partner", filtered_df)
    if partners:
        filtered_df = filtered_df[filtered_df["Partner"].isin(partners)]
    
    return filtered_df, "Tons"
