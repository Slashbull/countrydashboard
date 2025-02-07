# scenario_simulation.py
import streamlit as st
import pandas as pd

def simulate_scenario(df):
    st.header("Scenario Simulation")
    # Example: Adjust a growth factor and see the impact on tonnage
    growth_factor = st.slider("Select Growth Factor", 0.5, 2.0, 1.0, 0.1)
    df_sim = df.copy()
    if "Tons" in df_sim.columns:
        df_sim["Simulated_Tons"] = df_sim["Tons"] * growth_factor
        st.dataframe(df_sim.head())
