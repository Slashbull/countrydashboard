# reporting.py
import streamlit as st

def generate_report():
    from core_system import data  # Global data
    csv = data.to_csv(index=False).encode('utf-8')
    st.download_button("Download Report as CSV", data=csv, file_name="trade_report.csv", mime="text/csv")
