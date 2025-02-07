# authentication.py
import streamlit as st
import streamlit_authenticator as stauth
from config import AUTH_CREDENTIALS

def login():
    # Prepare credentials for streamlit_authenticator
    credentials = {
        "usernames": AUTH_CREDENTIALS["usernames"]
    }
    names = [AUTH_CREDENTIALS["usernames"][user]["name"] for user in AUTH_CREDENTIALS["usernames"]]
    usernames = list(AUTH_CREDENTIALS["usernames"].keys())
    # WARNING: For simplicity, passwords are in plain text here.
    # In production, use hashed passwords and secure storage.
    passwords = [AUTH_CREDENTIALS["usernames"][user]["password"] for user in AUTH_CREDENTIALS["usernames"]]

    authenticator = stauth.Authenticate(
        credentials,
        "trade_dashboard_cookie",  # cookie name
        "abcdef",                  # signature key (should be a secret)
        cookie_expiry_days=1
    )
    name, authentication_status, username = authenticator.login("Login", "main")

    if authentication_status:
        st.success(f"Welcome *{name}*")
        return True
    elif authentication_status is False:
        st.error("Username/password is incorrect")
        return False
    elif authentication_status is None:
        st.warning("Please enter your username and password")
        return False
