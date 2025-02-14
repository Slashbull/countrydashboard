import streamlit as st
import pandas as pd
from datetime import datetime

# Predefined order for months (abbreviations)
MONTH_ORDER = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

def convert_month_to_abbr(month):
    """
    Convert a numeric month or a string month to a three-letter abbreviation.
    If already an abbreviation, returns it as is.
    """
    try:
        # If the month is a digit (or string that can be converted to int), convert to abbreviation.
        month_int = int(month)
        # Use datetime to get the abbreviated month name.
        return datetime(1900, month_int, 1).strftime("%b")
    except (ValueError, TypeError):
        # Otherwise, assume it's already an abbreviated name (or some other string) and title-case it.
        return str(month).title()

def dynamic_multiselect(label: str, column: str, df: pd.DataFrame):
    """
    Create a sidebar multiselect widget for the specified column.
    
    For the "Month" column, numeric values will be converted to three-letter abbreviations
    using the convert_month_to_abbr() helper function, and then sorted by the predefined MONTH_ORDER.
    
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
    
    # Get unique non-null options.
    options = list(df[column].dropna().unique())
    
    if column == "Month":
        # Convert numeric month values to abbreviations.
        options = [convert_month_to_abbr(m) for m in options]
        # Remove duplicates and sort by the defined order.
        options = sorted(list(set(options)), key=lambda m: MONTH_ORDER.get(m, 99))
    else:
        options = sorted(options)
    
    # Create a multiselect widget with an empty default (interpreted as "select all")
    selected = st.sidebar.multiselect(f"{label}:", options, default=[], key=f"multiselect_{column}")
    return options if not selected else selected

def apply_filters(df: pd.DataFrame):
    """
    Display global filters (Year, Month, and Partner) in the sidebar and apply them.
    
    Returns:
        tuple: (filtered dataframe, "Tons")
    """
    st.sidebar.header("🔍 Global Filters")
    filtered_df = df.copy()
    
    # Filter by Year.
    years = dynamic_multiselect("Select Year", "Year", filtered_df)
    if years:
        filtered_df = filtered_df[filtered_df["Year"].isin(years)]
    
    # Filter by Month.
    months = dynamic_multiselect("Select Month", "Month", filtered_df)
    if months:
        # If the original month data was numeric, convert it for filtering.
        # We'll convert each month value in the dataframe using the same helper.
        filtered_df["Month_Abbr"] = filtered_df["Month"].apply(convert_month_to_abbr)
        filtered_df = filtered_df[filtered_df["Month_Abbr"].isin(months)]
    
    # Filter by Partner.
    partners = dynamic_multiselect("Select Partner", "Partner", filtered_df)
    if partners:
        filtered_df = filtered_df[filtered_df["Partner"].isin(partners)]
    
    return filtered_df, "Tons"
