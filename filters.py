import streamlit as st
import pandas as pd

# Predefined order for months (when using abbreviated month names)
MONTH_ORDER = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

def dynamic_multiselect(label: str, column: str, df: pd.DataFrame):
    """
    Create a sidebar multiselect widget for the specified column.
    
    If the column is "Month", options are sorted by a predefined order.
    If no selection is made, all available options are returned.
    
    Parameters:
        label (str): The label to display above the widget.
        column (str): The dataframe column to extract unique options.
        df (pd.DataFrame): The input dataframe.
        
    Returns:
        list: A list of selected values (or all values if none are selected).
    """
    if column not in df.columns:
        st.sidebar.error(f"Column '{column}' not found in data.")
        return []
    # Get unique non-null options and sort them
    options = list(df[column].dropna().unique())
    if column == "Month":
        options = sorted(options, key=lambda m: MONTH_ORDER.get(m, 99))
    else:
        options = sorted(options)
    # Create a multiselect widget with an empty default (meaning "select all" later)
    selected = st.sidebar.multiselect(f"{label}:", options, default=[], key=f"multiselect_{column}")
    # If nothing is selected, return all options (i.e. do not filter)
    return options if not selected else selected

def apply_filters(df: pd.DataFrame):
    """
    Display global filters (Year, Month, and Partner) in the sidebar and apply them.
    
    Returns:
        tuple: (filtered dataframe, "Tons")
    """
    st.sidebar.header("🔍 Global Filters")
    filtered_df = df.copy()
    
    # Filter by Year
    years = dynamic_multiselect("Select Year", "Year", filtered_df)
    if years:
        filtered_df = filtered_df[filtered_df["Year"].isin(years)]
    
    # Filter by Month
    months = dynamic_multiselect("Select Month", "Month", filtered_df)
    if months:
        filtered_df = filtered_df[filtered_df["Month"].isin(months)]
    
    # Filter by Partner
    partners = dynamic_multiselect("Select Partner", "Partner", filtered_df)
    if partners:
        filtered_df = filtered_df[filtered_df["Partner"].isin(partners)]
    
    return filtered_df, "Tons"
