import streamlit as st
import yaml

def login_user():
    st.sidebar.title("Login")
    email = st.sidebar.text_input("Email", key="login_email")
    if st.sidebar.button("Login"):
        with open("auth/allowed_users.yaml", "r") as f:
            users = yaml.safe_load(f)
        if email in users:
            st.session_state["user"] = {"email": email, "name": users[email]["name"]}
            return st.session_state["user"]
        else:
            st.error("Access denied.")
    return st.session_state.get("user", None)