# segmentation_analysis.py
import streamlit as st
import pandas as pd
import plotly.express as px

def segmentation_analysis_dashboard(data: pd.DataFrame):
    st.title("📊 Segmentation Analysis Dashboard")
    st.markdown("""
    This module provides segmentation analysis of your trade data by key dimensions.
    Explore trade volume by Flow (e.g., Import vs Export) and optionally by Reporter or Partner.
    """)

    # Validate required columns.
    required_cols = ["Flow", "Tons", "Reporter", "Partner"]
    missing = [col for col in required_cols if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing required columns: {', '.join(missing)}")
        return

    # Ensure "Tons" is numeric.
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")

    # Create a multi-tab layout for segmentation.
    tabs = st.tabs(["By Flow", "By Other Dimension"])
    
    ############################################################
    # Tab 1: Segmentation by Flow
    ############################################################
    with tabs[0]:
        st.header("Trade Volume by Flow")
        flow_seg = data.groupby("Flow", as_index=False)["Tons"].sum().sort_values("Tons", ascending=False)
        st.dataframe(flow_seg)
        
        # Pie Chart: Market Share by Flow.
        fig_flow_pie = px.pie(
            flow_seg,
            names="Flow",
            values="Tons",
            title="Market Share by Flow",
            hole=0.3,
            template="plotly_white"
        )
        st.plotly_chart(fig_flow_pie, use_container_width=True)
        
        # Bar Chart: Trade Volume by Flow.
        fig_flow_bar = px.bar(
            flow_seg,
            x="Flow",
            y="Tons",
            title="Trade Volume by Flow",
            text_auto=True,
            template="plotly_white"
        )
        st.plotly_chart(fig_flow_bar, use_container_width=True)

    ############################################################
    # Tab 2: Segmentation by an Additional Dimension (Reporter or Partner)
    ############################################################
    with tabs[1]:
        st.header("Additional Segmentation")
        dimension = st.selectbox("Select dimension for segmentation:", ["Reporter", "Partner"])
        if dimension not in data.columns:
            st.error(f"🚨 '{dimension}' column not found in data.")
            return
        
        seg_data = data.groupby(dimension, as_index=False)["Tons"].sum().sort_values("Tons", ascending=False)
        st.dataframe(seg_data)
        
        # Bar Chart: Trade Volume by the selected dimension.
        fig_seg_bar = px.bar(
            seg_data,
            x=dimension,
            y="Tons",
            title=f"Trade Volume by {dimension}",
            text_auto=True,
            template="plotly_white"
        )
        st.plotly_chart(fig_seg_bar, use_container_width=True)
        
        # Optional Pie Chart: Market Share by the selected dimension.
        seg_data["Share (%)"] = (seg_data["Tons"] / seg_data["Tons"].sum()) * 100
        fig_seg_pie = px.pie(
            seg_data,
            names=dimension,
            values="Tons",
            title=f"Market Share by {dimension}",
            hole=0.4,
            hover_data={"Share (%)":":.2f"},
            template="plotly_white"
        )
        st.plotly_chart(fig_seg_pie, use_container_width=True)

    st.success("✅ Segmentation Analysis Dashboard loaded successfully!")
