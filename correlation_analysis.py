# correlation_analysis.py
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from data_loader import load_data
from filters import add_filters

def show_correlation_analysis():
    st.header("Correlation Analysis")
    df = load_data()
    df = add_filters(df)
    
    # Compute correlation matrix for numeric columns
    corr_matrix = df.select_dtypes(include=['float64', 'int64']).corr()
    
    st.write("Correlation Matrix:")
    st.dataframe(corr_matrix)
    
    # Plot heatmap using seaborn
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax)
    st.pyplot(fig)
