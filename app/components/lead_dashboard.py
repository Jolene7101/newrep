import streamlit as st
import sqlite3
import yaml
import os
from scraper_engine import run_all_scrapers

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

    # Load user filters
    user_filters = {
        "valuation_min": row[1],
        "min_stories": row[2],
        "keywords": row[3]
    }

    # Load credentials for the user
    creds = {}
    if os.path.exists("auth/allowed_users.yaml"):
        with open("auth/allowed_users.yaml", "r") as f:
            users = yaml.safe_load(f)
            creds = users.get(user["email"], {})
    if not creds:
        st.error("No scraper credentials found for this user. Please contact admin.")
        return

    # Set enabled sources from filters table
    enabled_sources = {
        "gc_sites": bool(row[4]),
        "linkedin": bool(row[5]),
        "twitter": bool(row[6]),
        "google_news": bool(row[7]),
        "reddit": bool(row[8]),
    }
    proxy_override = row[9] if len(row) > 9 else None

    # Run scrapers and display results
    with st.spinner("Scraping latest projects... this may take up to a minute."):
        try:
            results = run_all_scrapers(user_filters, enabled_sources, creds, proxy_override)
        except Exception as e:
            st.error(f"Scraper error: {e}")
            return

    if not results:
        st.info("No projects matched your filters or scraping returned no results.")
        return

    st.success(f"Found {len(results)} projects:")
    for project in results:
        title = project.get('title', 'Untitled')
        source = project.get('source', 'Unknown')
        desc = project.get('description', '')
        st.markdown(f"- **{title}** ({source})<br/><span style='color: #64748b'>{desc[:120]}{'...' if len(desc)>120 else ''}</span>", unsafe_allow_html=True)