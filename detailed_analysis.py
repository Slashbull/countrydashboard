
# detailed_analysis.py
import streamlit as st
from filters import add_filters

def show_detailed_analysis():
    st.header("Detailed Analysis")
    # Get data from session_state (assume core_system.py stores it as 'uploaded_data')
    df = st.session_state.get("uploaded_data")
    if df is None or df.empty:
        st.warning("No data available.")
        return
    df_filtered = add_filters(df)
    st.write("Filtered Data Preview:")
    st.dataframe(df_filtered.head(20))
