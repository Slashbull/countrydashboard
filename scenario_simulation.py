# scenario_simulation.py
import streamlit as st
import pandas as pd

def simulate_scenario():
    st.header("Scenario Simulation")
    growth_factor = st.slider("Select Growth Factor", 0.5, 2.0, 1.0, 0.1)
    from core_system import data  # Global data
    df_sim = data.copy()
    if "Tons" in df_sim.columns:
        df_sim["Simulated_Tons"] = df_sim["Tons"] * growth_factor
        st.write("Simulated Data (first 10 rows):")
        st.dataframe(df_sim.head(10))
