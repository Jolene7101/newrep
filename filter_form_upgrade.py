import streamlit as st
import sqlite3

def show_filter_form(user):
    st.header("🔍 Your Project Filters")
    conn = sqlite3.connect("db/filters.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS filters (
        email TEXT PRIMARY KEY,
        valuation_min INTEGER,
        min_stories INTEGER,
        keywords TEXT,
        source_dodge INTEGER,
        source_linkedin INTEGER,
        source_gc INTEGER,
        days TEXT
    )""")

    valuation = st.slider("Min Project Value ($M)", 10, 500, 25)
    stories = st.slider("Min Number of Stories", 1, 20, 3)
    keywords = st.text_input("Keywords", "data center, fireproofing, steel")

    st.subheader("Sources")
    source_dodge = st.checkbox("Dodge Pipeline", value=True)
    source_linkedin = st.checkbox("LinkedIn", value=True)
    source_gc = st.checkbox("GC Websites", value=True)

    st.subheader("Alert Days")
    days = st.multiselect("Days to Receive Alerts", ["Mon", "Tue", "Wed", "Thu", "Fri"], default=["Mon", "Tue", "Wed", "Thu", "Fri"])

    if st.button("💾 Save Filters"):
        c.execute("REPLACE INTO filters VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                  (user["email"], valuation, stories, keywords, int(source_dodge), int(source_linkedin), int(source_gc), ",".join(days)))
        conn.commit()
        st.success("Filters saved.")
    conn.close()