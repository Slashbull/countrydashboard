# authentication.py
import streamlit as st
from config import SINGLE_USER

def login():
    """
    A simple single-user authentication system.
    Prompts for username and password, and checks against credentials in config.py.
    
    Returns:
        bool: True if login is successful, otherwise False.
    """
    # Initialize session state for authentication if not already set
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # If the user is not already logged in, display the login form
    if not st.session_state.logged_in:
        st.markdown("<h2 style='text-align: center;'>Login</h2>", unsafe_allow_html=True)
        username_input = st.text_input("Username", key="username_input")
        password_input = st.text_input("Password", type="password", key="password_input")
        
        if st.button("Login"):
            if username_input == SINGLE_USER["username"] and password_input == SINGLE_USER["password"]:
                st.success(f"Welcome, {SINGLE_USER['name']}!")
                st.session_state.logged_in = True
            else:
                st.error("🚨 Incorrect username or password. Please try again.")
    
    return st.session_state.logged_in
