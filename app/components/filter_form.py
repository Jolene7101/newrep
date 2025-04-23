import streamlit as st
import sqlite3
from proxy_ui import fetch_proxies, test_proxy

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

    st.subheader("Proxy Selection (Optional)")
    if st.button("Load Free Proxies", key="form_load_proxies"):
        st.session_state['form_proxies'] = fetch_proxies()
        st.session_state['form_proxy_health'] = {}
    proxies = st.session_state.get('form_proxies', [])
    proxy_health = st.session_state.get('form_proxy_health', {})
    if proxies:
        if st.button("Test All Proxies", key="form_test_proxies"):
            health = {}
            with st.spinner("Testing proxies..."):
                for p in proxies[:20]:
                    ok, msg = test_proxy(p)
                    health[p] = (ok, msg)
            st.session_state['form_proxy_health'] = health
            proxy_health = health
        display = []
        for p in proxies:
            status = proxy_health.get(p)
            if status is None:
                display.append(f"{p} (untested)")
            else:
                ok_tuple, msg = status
                emoji = "🟢" if ok_tuple[0] and ok_tuple[1] else ("🟡" if ok_tuple[0] or ok_tuple[1] else "🔴")
                display.append(f"{emoji} {p} [{msg}]")
        proxy = st.selectbox("Select a proxy for scraping:", proxies, format_func=lambda x: next((d for d in display if x in d), x), key="form_proxy_select", index=proxies.index(proxy) if proxy in proxies else 0)
    else:
        proxy = ""
        st.info("No proxies loaded. Click 'Load Free Proxies' to fetch.")

    if st.button("💾 Save Filters"):
        c.execute("REPLACE INTO filters VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (user["email"], valuation, stories, keywords, int(source_gc), int(source_linkedin), int(source_twitter), int(source_google_news), int(source_reddit), proxy))
        conn.commit()
        st.success("Filters saved.")
    conn.close()