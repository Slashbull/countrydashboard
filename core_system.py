# core_system.py (Phase 1: Authentication Test)
import streamlit as st
import config
from authentication import login

st.set_page_config(page_title=config.APP_TITLE, layout="wide")
st.title(config.APP_TITLE)

# Run authentication; if it fails, stop the app.
if not login():
    st.stop()

st.write("Authentication successful! (Phase 1 complete)")
