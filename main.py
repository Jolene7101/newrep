import streamlit as st
import os
import logging
from auth.auth import login_user
from app.components.filter_form import show_filter_form
from app.components.lead_dashboard import show_leads
from db_migration import migrate_database

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Check and migrate database if needed
try:
    migrate_result = migrate_database()
    if migrate_result:
        logger.info("Database schema is up to date")
    else:
        logger.warning("Using database in current state as migration was not necessary or failed")
except Exception as e:
    logger.error(f"Error during database migration check: {e}")

st.set_page_config(page_title="Hot Project Detector", layout="wide")
user = login_user()
if not user:
    st.stop()

st.title(f"🔥 Welcome, {user['name']}")
show_filter_form(user)
show_leads(user)