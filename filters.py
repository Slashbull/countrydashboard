import streamlit as st
import pandas as pd
import logging

# Setup logging for this module
logger = logging.getLogger(__name__)

# Define the order for month abbreviations to ensure proper sorting.
MONTH_ORDER = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

def dynamic_multiselect(label: str, column: str, df: pd.DataFrame):
    """
    Create a sidebar multiselect widget for the specified column in the dataframe.
    
    Parameters:
        label (str): The label to display.
        column (str): The column name from which to generate options.
        df (pd.DataFrame): The data frame to pull options from.
    
    Returns:
        list: The list of selected options.
    """
    if column not in df.columns:
        st.sidebar.error(f"Column '{column}' not found in data.")
        logger.error("Column '%s' missing in data.", column)
        return []
    
    options = df[column].dropna().unique().tolist()
    # Sort months based on predefined order if the column is 'Month'
    if column == "Month":
        options = sorted(options, key=lambda m: MONTH_ORDER.get(m, 99))
    else:
        options = sorted(options)
    
    # By default, we set all options as selected
    selected = st.sidebar.multiselect(f"📌 {label}:", options, default=options, key=f"multiselect_{column}")
    return selected

def apply_filters(df: pd.DataFrame):
    """
    Display and apply global filters from the sidebar for the dataframe.
    Currently, filters for Year, Month, and Partner are implemented.
    
    Parameters:
        df (pd.DataFrame): The input dataframe.
        
    Returns:
        tuple: (filtered dataframe, unit column name)
    """
    st.sidebar.header("🔍 Global Data Filters")
    filtered_df = df.copy()
    
    # Apply Year filter.
    selected_years = dynamic_multiselect("Select Year", "Year", filtered_df)
    if selected_years:
        filtered_df = filtered_df[filtered_df["Year"].isin(selected_years)]
    
    # Apply Month filter.
    selected_months = dynamic_multiselect("Select Month", "Month", filtered_df)
    if selected_months:
        filtered_df = filtered_df[filtered_df["Month"].isin(selected_months)]
    
    # Apply Partner filter.
    selected_partners = dynamic_multiselect("Select Partner", "Partner", filtered_df)
    if selected_partners:
        filtered_df = filtered_df[filtered_df["Partner"].isin(selected_partners)]
    
    # Log the filtering action.
    logger.info("Filters applied: Years=%s, Months=%s, Partners=%s", selected_years, selected_months, selected_partners)
    
    # Return the filtered dataframe and the unit of measurement (assumed "Tons").
    return filtered_df, "Tons"
