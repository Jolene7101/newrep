import streamlit as st
import sqlite3
from ui import display_dashboard_card, styled_container

def show_email_logs():
    st.title("📬 Email Logs")
    conn = sqlite3.connect("db/email_logs.db")
    c = conn.cursor()
    c.execute("SELECT email, subject, lead_count, sources, status, timestamp FROM email_logs ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()

    if not rows:
        st.info("No emails logged yet.")
        return

    display_dashboard_card("Total Emails Sent", len(rows))
    for row in rows[:10]:  # show latest 10
        email, subject, leads, sources, status, ts = row
        status_color = "#16a34a" if status == "sent" else "#dc2626"
        content = f"""
        <b>To:</b> {email}<br>
        <b>Subject:</b> {subject}<br>
        <b>Leads:</b> {leads} | <b>Sources:</b> {sources}<br>
        <b>Status:</b> <span style='color: {status_color}; font-weight: bold;'>{status}</span><br>
        <small>{ts}</small>
        """
        styled_container("Email Summary", content)