# core_system.py (Phase 2: Authentication + Data Upload)
import streamlit as st
import config
from authentication import login
from data_loader import upload_data

st.set_page_config(page_title=config.APP_TITLE, layout="wide")
st.title(config.APP_TITLE)

# Authentication
if not login():
    st.stop()

# Data Upload & Storage
if "uploaded_data" not in st.session_state or st.sidebar.button("Reset Data"):
    df = upload_data()
    st.session_state["uploaded_data"] = df
else:
    df = st.session_state["uploaded_data"]

if df.empty:
    st.warning("No data loaded. Please upload your CSV or provide a Google Sheet link.")
    st.stop()
else:
    st.write("Data loaded successfully!")
    st.write("Preview of the data:")
    st.dataframe(df.head())
