# scenario_simulation.py
import streamlit as st
import pandas as pd
import numpy as np

def scenario_simulation_dashboard(data: pd.DataFrame):
    st.header("🔄 Scenario Simulation")
    st.markdown("Adjust parameters to simulate different trade scenarios.")
    growth_rate = st.slider("Expected Growth Rate (%)", -10, 50, 5)
    base_volume = data["Tons"].sum()
    simulated_volume = base_volume * (1 + growth_rate/100)
    st.metric("Simulated Future Volume", f"{simulated_volume:,.2f}")
