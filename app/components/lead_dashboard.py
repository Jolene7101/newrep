import streamlit as st
import sqlite3

def show_leads(user):
    st.header("📋 Your Matched Projects")
    conn = sqlite3.connect("db/filters.db")
    c = conn.cursor()
    c.execute("SELECT * FROM filters WHERE email = ?", (user["email"],))
    row = c.fetchone()
    conn.close()

    if not row:
        st.warning("No filters set.")
        return

    st.info("🚧 Demo Data — real scraper integration pending.")
    st.markdown("- **Dallas Medical Tower** – 12 stories – $180M – Type I steel")
    st.markdown("- **Houston Airport Expansion** – 8 stories – $120M – Fireproofing in specs")