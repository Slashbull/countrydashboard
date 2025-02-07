# detailed_analysis.py
import streamlit as st
import pandas as pd
import plotly.express as px

def detailed_analysis_dashboard(data: pd.DataFrame):
    st.header("🔍 Detailed Analysis")
    
    st.markdown("### Top Reporters by Volume")
    reporter_summary = data.groupby("Reporter")["Tons"].sum().reset_index()
    reporter_summary = reporter_summary.sort_values("Tons", ascending=False)
    st.dataframe(reporter_summary)
    
    fig = px.bar(reporter_summary, x="Reporter", y="Tons", title="Volume by Reporter", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)
