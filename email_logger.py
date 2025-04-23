import sqlite3
from datetime import datetime

def init_log_db():
    conn = sqlite3.connect("db/email_logs.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS email_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        subject TEXT,
        lead_count INTEGER,
        sources TEXT,
        status TEXT,
        timestamp TEXT,
        message_id TEXT
    )""")
    conn.commit()
    conn.close()

def log_email_send(email, subject, lead_count, sources, status, message_id="-"):
    conn = sqlite3.connect("db/email_logs.db")
    c = conn.cursor()
    c.execute("INSERT INTO email_logs (email, subject, lead_count, sources, status, timestamp, message_id) VALUES (?, ?, ?, ?, ?, ?, ?)", (
        email, subject, lead_count, sources, status, datetime.utcnow().isoformat(), message_id
    ))
    conn.commit()
    conn.close()