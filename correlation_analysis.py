# correlation_analysis.py
import streamlit as st
import pandas as pd
import plotly.express as px

def correlation_analysis_dashboard(data: pd.DataFrame):
    st.title("🔗 Correlation Analysis Dashboard")
    st.markdown("""
    Explore correlations between numeric variables in your trade data.
    This analysis can help you identify which factors tend to move together.
    """)

    # Select numeric columns
    numeric_cols = data.select_dtypes(include=["number"]).columns.tolist()
    if not numeric_cols:
        st.error("No numeric columns found for correlation analysis.")
        return

    # Compute correlation matrix
    corr_matrix = data[numeric_cols].corr()
    st.markdown("#### Correlation Matrix Data")
    st.dataframe(corr_matrix)

    # Create a heatmap for the correlation matrix.
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        title="Correlation Matrix Heatmap",
        color_continuous_scale=px.colors.sequential.Viridis
    )
    st.plotly_chart(fig, use_container_width=True)

    st.success("✅ Correlation Analysis Dashboard loaded successfully!")
