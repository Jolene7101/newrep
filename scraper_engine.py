from linkedin_scraper import scrape_linkedin_posts
from gc_scraper import scrape_gc_site
from twitter_scraper import scrape_twitter_posts
from google_news_scraper import scrape_google_news
from reddit_scraper import scrape_reddit_posts

def run_all_scrapers(user_filters, enabled_sources, creds):
    all_projects = []

    if enabled_sources.get("linkedin"):
        linkedin_projects = scrape_linkedin_posts(user_filters["keywords"].split(","))
        all_projects.extend(linkedin_projects)

    if enabled_sources.get("gc_sites"):
        for gc_name in ["JE Dunn", "Turner", "Skanska"]:
            gc_projects = scrape_gc_site(gc_name)
            all_projects.extend(gc_projects)

    if enabled_sources.get("twitter"):
        twitter_projects = scrape_twitter_posts(user_filters["keywords"].split(","))
        all_projects.extend(twitter_projects)

    if enabled_sources.get("google_news"):
        google_news_projects = scrape_google_news(user_filters["keywords"].split(","))
        all_projects.extend(google_news_projects)

    if enabled_sources.get("reddit"):
        # Example subreddit list; you may want to make this configurable
        subreddits = ["construction", "architecture", "engineering"]
        reddit_projects = scrape_reddit_posts(subreddits, user_filters["keywords"].split(","))
        all_projects.extend(reddit_projects)

    return all_projects