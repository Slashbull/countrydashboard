# correlation_analysis.py
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt

def show_correlation_analysis():
    st.header("Correlation Analysis")
    from core_system import data  # Global data
    from filters import add_filters
    df_filtered = add_filters(data)
    corr_matrix = df_filtered.select_dtypes(include=['float64', 'int64']).corr()
    st.write("Correlation Matrix:")
    st.dataframe(corr_matrix)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax)
    st.pyplot(fig)
