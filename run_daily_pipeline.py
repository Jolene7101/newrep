import yaml
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
            valuation_min INTEGER,
            min_stories INTEGER,
            keywords TEXT
        )''')
        # Optional: Seed a test user
        c.execute('''
        INSERT INTO filters (email, valuation_min, min_stories, keywords)
        VALUES (?, ?, ?, ?)''', (
            "test@example.com", 25, 3, "data center, fireproofing, steel"
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
