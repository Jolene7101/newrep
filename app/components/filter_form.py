import streamlit as st
import sqlite3
from proxy_ui import fetch_proxies, test_proxy

# US states with their abbreviations for state input validation
US_STATES = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming"
}

def normalize_states_input(states_input):
    """Normalize state input to a comma-separated list of state abbreviations."""
    if not states_input:
        return ""
        
    states_list = [s.strip() for s in states_input.split(',')]
    normalized_states = []
    
    for state in states_list:
        state = state.strip()
        # If it's a valid abbreviation
        if state.upper() in US_STATES:
            normalized_states.append(state.upper())
        # If it's a full state name
        else:
            for abbr, name in US_STATES.items():
                if name.lower() == state.lower():
                    normalized_states.append(abbr)
                    break
    
    return ",".join(normalized_states)

def show_filter_form(user):
    st.header("🔍 Your Project Filters")
    conn = sqlite3.connect("db/filters.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS filters (
        email TEXT PRIMARY KEY,
        states TEXT,
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
    states = row[1] if row else "TX,CA,NY"
    keywords = row[2] if row else "data center, fireproofing, steel"
    source_gc = bool(row[3]) if row else True
    source_linkedin = bool(row[4]) if row else True
    source_twitter = bool(row[5]) if row else True
    source_google_news = bool(row[6]) if row else True
    source_reddit = bool(row[7]) if row else True
    proxy = row[8] if row and len(row) > 8 else ""

    # Create a formatted version for display that shows both abbr and name
    states_display = ""
    if states:
        state_parts = []
        for abbr in states.split(','):
            if abbr in US_STATES:
                state_parts.append(f"{abbr} ({US_STATES[abbr]})")
        states_display = ", ".join(state_parts)

    # States input with help text
    st.write("Enter states to filter leads (comma-separated, use abbreviations or full names)")
    states_input = st.text_input("States", states if not states_display else states_display)
    
    # Show examples of valid inputs
    st.caption("Examples: 'TX, California, NY' or 'Texas, CA, New York'")
    
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
        # Normalize states input
        normalized_states = normalize_states_input(states_input)
        
        c.execute("REPLACE INTO filters VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (user["email"], normalized_states, keywords, int(source_gc), int(source_linkedin), int(source_twitter), int(source_google_news), int(source_reddit), proxy))
        conn.commit()
        st.success("Filters saved.")
    conn.close()