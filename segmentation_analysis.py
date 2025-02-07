# segmentation_analysis.py
import streamlit as st
import altair as alt
from sklearn.cluster import KMeans

def show_segmentation_analysis():
    st.header("Segmentation Analysis")
    from core_system import data  # Global data
    from filters import add_filters
    df_filtered = add_filters(data)
    df_features = df_filtered[['Tons']].fillna(0)
    kmeans = KMeans(n_clusters=3, random_state=42)
    df_filtered['Cluster'] = kmeans.fit_predict(df_features)
    
    st.write("Cluster assignments (first 10 rows):")
    st.dataframe(df_filtered[['Date', 'Partner', 'Tons', 'Cluster']].head(10))
    
    cluster_chart = alt.Chart(df_filtered).mark_circle(size=60).encode(
        x='Date:T',
        y='Tons:Q',
        color='Cluster:N',
        tooltip=['Date:T', 'Partner', 'Tons', 'Cluster']
    ).properties(width=700, height=400)
    st.altair_chart(cluster_chart, use_container_width=True)
