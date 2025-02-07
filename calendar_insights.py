# calendar_insights.py
import streamlit as st
import pandas as pd
import plotly.express as px

def calendar_insights_dashboard(data: pd.DataFrame):
    st.header("🗓 Calendar Insights")
    if "Period_dt" not in data.columns:
        st.error("Date column missing. Ensure data is preprocessed.")
        return
    data["Month_Name"] = data["Period_dt"].dt.strftime("%B")
    monthly = data.groupby("Month_Name")["Tons"].sum().reset_index()
    fig = px.bar(monthly, x="Month_Name", y="Tons", title="Volume by Month")
    st.plotly_chart(fig, use_container_width=True)
