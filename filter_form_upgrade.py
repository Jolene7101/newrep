import streamlit as st
import sqlite3

def show_filter_form(user):
    st.header("🔍 Your Project Filters")
    conn = import yaml
import sqlite3
from scraper_engine import run_all_scrapers
from filter_engine import filter_leads
from mailer.send_mail import send_email
from email_formatter import format_email_body

def run_daily_pipeline():
    print("🚀 Starting daily pipeline...")
    
    with open("auth/allowed_users.yaml") as f:
        user_data = yaml.safe_load(f)

    conn = sqlite3.connect("/db/filters.db")

    c = conn.cursor()

    # ✅ Ensure the filters table exists BEFORE querying it
    c.execute('''
    CREATE TABLE IF NOT EXISTS filters (
        email TEXT PRIMARY KEY,
        valuation_min INTEGER,
        min_stories INTEGER,
        keywords TEXT
    )
    ''')
    conn.commit()

    for email, user_info in user_data.items():
        print(f"👤 Checking filters for: {email}")
        c.execute("SELECT * FROM filters WHERE email = ?", (email,))
        row = c.fetchone()
        if not row:
            print(f"⚠️ No filters found for {email}")
            continue

        user_filters = {
            "valuation_min": row[1],
            "min_stories": row[2],
            "keywords": row[3]
        }
        print(f"✅ Found filters: {user_filters}")

        enabled_sources = {"dodge": True, "linkedin": True, "gc_sites": True}
        creds = {"DODGE_EMAIL": email, "DODGE_PASSWORD": user_info.get("password", "")}

        all_projects = run_all_scrapers(user_filters, enabled_sources, creds)
        print(f"🔎 Scraped {len(all_projects)} total projects")

        matched = filter_leads(all_projects, user_filters)
        print(f"✅ {len(matched)} projects matched filters")

        for proj in matched:
            print(f"📌 Match: {proj.get('title')}")

        msg = format_email_body(user_info["name"], matched)
        send_email(
            to_email=email,
            subject="🔥 Your Daily Project Matches",
            text=msg,
            mailgun_api_key=user_info["mailgun_api"],
            domain=user_info["mailgun_domain"]
        )
        print(f"📧 Email sent to {email}")

    conn.close()
    print("✅ Daily pipeline complete.")

# Run if script is executed directly
if __name__ == "__main__":
    run_daily_pipeline()


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