# segmentation_analysis.py
import streamlit as st
import pandas as pd
import plotly.express as px

def segmentation_analysis_dashboard(data: pd.DataFrame):
    st.header("📊 Segmentation Analysis")
    if "Flow" not in data.columns:
        st.error("Flow column missing.")
        return
    flow_seg = data.groupby("Flow")["Tons"].sum().reset_index()
    fig = px.pie(flow_seg, names="Flow", values="Tons", title="Volume by Flow", hole=0.3)
    st.plotly_chart(fig, use_container_width=True)
