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
        source_gc INTEGER,
        source_linkedin INTEGER,
        source_twitter INTEGER,
        source_google_news INTEGER,
        source_reddit INTEGER,
        proxy TEXT
    )""")

    # Load existing values if present
    c.execute("SELECT * FROM filters WHERE email = ?", (user["email"],))
    row = c.fetchone()
    valuation = row[1] if row else 25
    stories = row[2] if row else 3
    keywords = row[3] if row else "data center, fireproofing, steel"
    source_gc = bool(row[4]) if row else True
    source_linkedin = bool(row[5]) if row else True
    source_twitter = bool(row[6]) if row else True
    source_google_news = bool(row[7]) if row else True
    source_reddit = bool(row[8]) if row else True
    proxy = row[9] if row and len(row) > 9 else ""

    valuation = st.slider("Min Project Value ($M)", 10, 500, valuation)
    stories = st.slider("Min Number of Stories", 1, 20, stories)
    keywords = st.text_input("Keywords (comma-separated)", keywords)
    st.subheader("Source Selection")
    source_gc = st.checkbox("GC Websites", value=source_gc)
    source_linkedin = st.checkbox("LinkedIn", value=source_linkedin)
    source_twitter = st.checkbox("Twitter", value=source_twitter)
    source_google_news = st.checkbox("Google News", value=source_google_news)
    source_reddit = st.checkbox("Reddit", value=source_reddit)

    st.subheader("Proxy (Optional)")
    proxy = st.text_input("Proxy (leave blank for none or use selector in main UI)", value=proxy)
    st.info("You can also use the proxy selector in the main dashboard UI.")

    if st.button("💾 Save Filters"):
        c.execute("REPLACE INTO filters VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (user["email"], valuation, stories, keywords, int(source_gc), int(source_linkedin), int(source_twitter), int(source_google_news), int(source_reddit), proxy))
        conn.commit()
        st.success("Filters saved.")
    conn.close()