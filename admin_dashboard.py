import streamlit as st
import sqlite3

def show_admin_dashboard():
    st.title("📊 Admin Dashboard – Email & Lead Monitoring")

    st.subheader("📝 Email Logs (Demo Data)")
    st.markdown("- ✅ test@example.com – Sent at 8:01 AM")
    st.markdown("- ❌ jane@company.com – Failed (SMTP error)")

    st.subheader("📥 Lead Volume by Source (Demo)")
    st.bar_chart({
        "Dodge": [14],
        "LinkedIn": [7],
        "GC Sites": [10]
    })

    st.subheader("👤 Rep Filter Summary")
    conn = sqlite3.connect("db/filters.db")
    c = conn.cursor()
    c.execute("SELECT * FROM filters")
    rows = c.fetchall()
    conn.close()

    for row in rows:
        st.markdown(f"**{row[0]}** — ${row[1]/1_000_000:.1f}M min, {row[2]}+ stories, Days: {row[7]}")