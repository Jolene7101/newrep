import streamlit as st

def styled_container(title, content):
    st.markdown(f"""
    <div style='background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem; margin-bottom: 1rem; box-shadow: 0 1px 2px rgba(0,0,0,0.05);'>
        <h3 style='color: #1e293b; font-size: 1.25rem; margin-bottom: 0.5rem;'>{title}</h3>
        <div style='color: #334155; font-size: 1rem;'>{content}</div>
    </div>
    """, unsafe_allow_html=True)

def display_dashboard_card(title, value, icon="📊"):
    st.markdown(f"""
    <div style='display: flex; align-items: center; background-color: #f1f5f9; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
        <span style='font-size: 1.5rem; margin-right: 1rem;'>{icon}</span>
        <div>
            <div style='font-weight: 600; color: #0f172a;'>{value}</div>
            <div style='color: #475569;'>{title}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)