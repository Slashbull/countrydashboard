# segmentation_analysis.py
import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
import altair as alt
from data_loader import load_data
from filters import add_filters

def show_segmentation_analysis():
    st.header("Segmentation Analysis")
    df = load_data()
    df = add_filters(df)
    # For example, cluster by Tonnage and Month (you can add more features)
    df_features = df[['Tons']].fillna(0)
    kmeans = KMeans(n_clusters=3, random_state=42)
    df['Cluster'] = kmeans.fit_predict(df_features)
    
    st.write("Cluster assignments:")
    st.dataframe(df[['Date', 'Partner', 'Tons', 'Cluster']].head(10))
    
    # Visualize clusters using Altair (if we use only Tonnage, it's one-dimensional,
    # so we add a jitter on the x-axis using Date)
    chart = alt.Chart(df).mark_circle(size=60).encode(
        x='Date:T',
        y='Tons:Q',
        color='Cluster:N',
        tooltip=['Date:T', 'Partner', 'Tons', 'Cluster']
    ).properties(width=700, height=400)
    
    st.altair_chart(chart, use_container_width=True)
