from linkedin_scraper import scrape_linkedin_posts
from gc_scraper import scrape_gc_site
from twitter_scraper import scrape_twitter_posts
from google_news_scraper import scrape_google_news
from reddit_scraper import scrape_reddit_posts
import streamlit as st

# Optionally, set your proxy and praw credentials here or pass from config
PROXY = None  # e.g., 'http://username:password@proxyhost:port'
PRAW_CREDS = None  # e.g., {'client_id': '...', 'client_secret': '...', 'user_agent': '...', ...}

def get_active_proxy():
    # Try to get proxy from Streamlit session state if running via UI
    try:
        return st.session_state.get('pipeline_proxy', PROXY)
    except Exception:
        return PROXY

def run_all_scrapers(user_filters, enabled_sources, creds, proxy_override=None):
    all_projects = []
    proxy = proxy_override if proxy_override else get_active_proxy()
    
    # Safely handle keyword splitting by ensuring it's a string first
    keywords = str(user_filters.get("keywords", "")).split(",")
    # Clean up keywords
    keywords = [k.strip() for k in keywords if k.strip()]

    if enabled_sources.get("linkedin"):
        linkedin_projects = scrape_linkedin_posts(keywords)
        all_projects.extend(linkedin_projects)

    if enabled_sources.get("gc_sites"):
        for gc_name in ["JE Dunn", "Turner", "Skanska"]:
            gc_projects = scrape_gc_site(gc_name, proxy=proxy, ignore_ssl=True)
            all_projects.extend(gc_projects)

    if enabled_sources.get("twitter"):
        twitter_projects = scrape_twitter_posts(keywords)
        all_projects.extend(twitter_projects)

    if enabled_sources.get("google_news"):
        google_news_projects = scrape_google_news(keywords, proxy=proxy)
        all_projects.extend(google_news_projects)

    if enabled_sources.get("reddit"):
        subreddits = ["construction", "architecture", "engineering"]
        reddit_projects = scrape_reddit_posts(
            subreddits,
            keywords,
            proxy=proxy,
            praw_creds=PRAW_CREDS
        )
        all_projects.extend(reddit_projects)

    return all_projects