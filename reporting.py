# reporting.py
import streamlit as st

def generate_report(df):
    st.download_button(
        label="Download Report as CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name="trade_report.csv",
        mime="text/csv"
    )
