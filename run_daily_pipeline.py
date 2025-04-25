import yaml
import certifi
import os
import urllib3
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['SSL_CERT_FILE'] = certifi.where()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import sqlite3

from scraper_engine import run_all_scrapers
from filter_engine import filter_leads
from mailer.send_mail import send_email
from email_formatter import format_email_body
import os

DB_PATH = "db/filters.db"

def init_db_if_missing():
    if not os.path.exists(DB_PATH):
        print("⚠️ filters.db not found — creating new one.")
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
        CREATE TABLE filters (
            email TEXT PRIMARY KEY,
            states TEXT,
            keywords TEXT,
            source_gc INTEGER,
            source_linkedin INTEGER,
            source_twitter INTEGER,
            source_google_news INTEGER,
            source_reddit INTEGER,
            proxy TEXT
        )''')
        # Optional: Seed a test user
        c.execute('''
        INSERT INTO filters (email, states, keywords, source_gc, source_linkedin, source_twitter, source_google_news, source_reddit, proxy)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            "test@example.com", "TX,CA,NY", "data center, fireproofing, steel", 1, 1, 1, 1, 1, ""
        ))
        conn.commit()
        conn.close()
    else:
        print("✅ filters.db found — using existing.")

def run_daily_pipeline():
    print("🚀 Starting daily pipeline...")
    init_db_if_missing()

    with open("auth/allowed_users.yaml") as f:
        user_data = yaml.safe_load(f)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    for email, user_info in user_data.items():
        print(f"👤 Checking filters for: {email}")
        c.execute("SELECT * FROM filters WHERE email = ?", (email,))
        row = c.fetchone()
        if not row:
            print(f"⚠️ No filters found for {email}")
            continue

        user_filters = {
            "states": row[1] if row else "",
            "keywords": row[2] if row else ""
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
        mailgun_api_key = user_info.get("mailgun_api")
        if not mailgun_api_key:
            raise KeyError(f"mailgun_api key missing for user {user_info.get('email', 'unknown')}. Please check allowed_users.yaml or credentials source.")
        send_email(
            to_email=email,
            subject="🔥 Your Daily Project Matches",
            text=msg,
            mailgun_api_key=mailgun_api_key,
            domain=user_info["mailgun_domain"]
        )
        print(f"📧 Email sent to {email}")

    conn.close()
    print("✅ Daily pipeline complete.")

# Run if script is executed directly
if __name__ == "__main__":
    run_daily_pipeline()
