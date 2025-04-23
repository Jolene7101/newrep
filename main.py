import streamlit as st
from auth.auth import login_user
from components.filter_form import show_filter_form
from components.lead_dashboard import show_leads

st.set_page_config(page_title="Hot Project Detector", layout="wide")
user = login_user()
if not user:
    st.stop()

st.title(f"🔥 Welcome, {user['name']}")
show_filter_form(user)
show_leads(user)