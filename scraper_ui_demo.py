import streamlit as st
import yaml
from scraper_engine import run_all_scrapers

st.title("🧪 Scraper Runner (Demo)")

st.sidebar.header("Select Sources")
enabled_sources = {
    "dodge": st.sidebar.checkbox("Dodge Pipeline", value=True),
    "linkedin": st.sidebar.checkbox("LinkedIn", value=True),
    "gc_sites": st.sidebar.checkbox("GC Websites", value=True)
}

st.sidebar.header("Filters")
keywords = st.sidebar.text_input("Keywords", "fireproofing, steel, UL, Type I")

if st.button("🔍 Run All Scrapers"):
    with open("auth/allowed_users.yaml") as f:
        creds = yaml.safe_load(f).get("test@example.com", {})

    user_filters = {
        "valuation_min": 25000000,
        "min_stories": 3,
        "keywords": keywords
    }

    results = run_all_scrapers(user_filters, enabled_sources, creds)
    st.success(f"Found {len(results)} projects")
    for project in results:
        st.markdown(f"- **{project['title']}** ({project.get('source', 'Unknown')})")