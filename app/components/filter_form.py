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
        keywords TEXT
    )""")
    
    valuation = st.slider("Min Project Value ($M)", 10, 500, 25)
    stories = st.slider("Min Number of Stories", 1, 20, 3)
    keywords = st.text_input("Keywords (comma-separated)", "data center, fireproofing, steel")

    if st.button("💾 Save Filters"):
        c.execute("REPLACE INTO filters VALUES (?, ?, ?, ?)", 
                  (user["email"], valuation, stories, keywords))
        conn.commit()
        st.success("Filters saved.")
    conn.close()