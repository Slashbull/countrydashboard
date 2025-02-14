# detailed_analysis.py
import streamlit as st
import pandas as pd
import plotly.express as px

def detailed_analysis_dashboard(data: pd.DataFrame):
    st.title("🔍 Detailed Analysis")

    # Validate required columns
    required_cols = ["Reporter", "Partner", "Tons", "Year", "Month", "Period"]
    missing = [col for col in required_cols if col not in data.columns]
    if missing:
        st.error(f"🚨 Missing required columns: {', '.join(missing)}")
        return

    # Ensure that "Tons" is numeric
    data["Tons"] = pd.to_numeric(data["Tons"], errors="coerce")

    # Create two main tabs: Summary and Drill Down
    tabs = st.tabs(["Summary", "Drill Down"])

    # ----- Tab 1: Summary -----
    with tabs[0]:
        st.header("Summary: Trade Volume by Reporter")
        # Aggregate trade volume by Reporter
        reporter_summary = data.groupby("Reporter")["Tons"].sum().reset_index()
        reporter_summary = reporter_summary.sort_values("Tons", ascending=False)
        st.dataframe(reporter_summary)

        # Bar chart for visualization
        fig_bar = px.bar(
            reporter_summary,
            x="Reporter",
            y="Tons",
            title="Volume by Reporter",
            text_auto=True,
            template="plotly_white"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ----- Tab 2: Drill Down Analysis -----
    with tabs[1]:
        st.header("Drill Down Analysis")
        # Allow user to select a dimension for drill down (Reporter or Partner)
        dimension = st.radio("Select Dimension for Drill Down:", ("Reporter", "Partner"), index=0)
        entities = sorted(data[dimension].dropna().unique().tolist())
        selected_entity = st.selectbox(f"Select {dimension}:", entities)
        detail_data = data[data[dimension] == selected_entity]
        st.subheader(f"Trade Data for {dimension}: {selected_entity}")
        st.dataframe(detail_data)

        # Pivot Table: Aggregate trade volume by Period for the selected entity
        st.markdown("##### Pivot Table: Volume by Period")
        pivot = detail_data.pivot_table(
            index=dimension,
            columns="Period",
            values="Tons",
            aggfunc="sum",
            fill_value=0
        )
        st.dataframe(pivot)

        # Trend Analysis: Line chart of trade volume over periods
        st.markdown("##### Trend Analysis")
        entity_trend = detail_data.groupby("Period", as_index=False)["Tons"].sum()
        # Ensure ordering using the categorical Period column
        entity_trend = entity_trend.sort_values("Period")
        fig_line = px.line(
            entity_trend,
            x="Period",
            y="Tons",
            title=f"Trade Volume Trend for {selected_entity}",
            markers=True,
            template="plotly_white"
        )
        st.plotly_chart(fig_line, use_container_width=True)

        st.success("Drill Down Analysis loaded successfully!")

    st.success("✅ Detailed Analysis Dashboard loaded successfully!")
