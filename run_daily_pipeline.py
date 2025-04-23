import yaml
import sqlite3
from scraper_engine import run_all_scrapers
from filter_engine import filter_leads
from mailer.send_mail import send_email
from email_formatter import format_email_body

def run_daily_pipeline():
    with open("auth/allowed_users.yaml") as f:
        user_data = yaml.safe_load(f)

    conn = sqlite3.connect("db/filters.db")
    c = conn.cursor()

    for email, user_info in user_data.items():
        c.execute("SELECT * FROM filters WHERE email = ?", (email,))
        row = c.fetchone()
        if not row:
            continue

        user_filters = {
            "valuation_min": row[1],
            "min_stories": row[2],
            "keywords": row[3]
        }

        enabled_sources = {"dodge": True, "linkedin": True, "gc_sites": True}
        creds = {"DODGE_EMAIL": email, "DODGE_PASSWORD": user_info.get("password", "")}

        all_projects = run_all_scrapers(user_filters, enabled_sources, creds)
        matched = filter_leads(all_projects, user_filters)

        msg = format_email_body(user_info["name"], matched)
        send_email(
            to_email=email,
            subject="🔥 Your Daily Project Matches",
            text=msg,
            mailgun_api_key=user_info["mailgun_api"],
            domain=user_info["mailgun_domain"]
        )

    conn.close()