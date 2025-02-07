# reporting.py
import streamlit as st
import pandas as pd

def reporting_dashboard(data: pd.DataFrame):
    st.header("📑 Reporting & Exports")
    st.markdown("Preview the top rows and download the data as CSV.")
    st.dataframe(data.head(50))
    csv = data.to_csv(index=False).encode('utf-8')
    st.download_button("Download Data as CSV", csv, "trade_report.csv", "text/csv")
