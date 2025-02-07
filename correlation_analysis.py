# correlation_analysis.py
import streamlit as st
import pandas as pd
import plotly.express as px

def correlation_analysis_dashboard(data: pd.DataFrame):
    st.header("🔗 Correlation Analysis")
    numeric_cols = data.select_dtypes(include=["number"]).columns.tolist()
    if not numeric_cols:
        st.error("No numeric columns found for correlation analysis.")
        return
    corr_matrix = data[numeric_cols].corr()
    st.dataframe(corr_matrix)
    fig = px.imshow(corr_matrix, text_auto=True, title="Correlation Matrix")
    st.plotly_chart(fig, use_container_width=True)
