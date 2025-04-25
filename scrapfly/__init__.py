"""
Scrapfly-based Fireproofing Lead Scraper (Free Tier Compatible)

A modular system for extracting construction and fireproofing-related leads
from various online sources using the Scrapfly API free tier.
"""
import logging
from typing import List, Dict, Any

from .linkedin_scraper import scrape_linkedin_posts
from .twitter_scraper import scrape_twitter_posts
from .reddit_scraper import scrape_reddit_posts
from .google_news_scraper import scrape_google_news
from .utils import save_results

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

__all__ = [
    'scrape_linkedin_posts',
    'scrape_twitter_posts',
    'scrape_reddit_posts',
    'scrape_google_news',
    'save_results',
    'run_all_scrapers'
]

def run_all_scrapers(
    keywords: List[str],
    sources: List[str] = ["google_news", "reddit", "twitter", "linkedin"],
    limit: int = 10,
    subreddits: List[str] = ["construction", "architecture", "engineering"],
    linkedin_urls: List[str] = None
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Run all scrapers to gather fireproofing and construction leads from specified sources.
    
    Args:
        keywords: List of fireproofing keywords to search for
        sources: List of sources to scrape (google_news, reddit, twitter, linkedin)
        limit: Maximum number of results per source
        subreddits: List of subreddits to search for Reddit
        linkedin_urls: Optional list of specific LinkedIn post URLs to scrape
        
    Returns:
        Dictionary with source names as keys and lists of results as values
    """
    results = {}
    all_results = []
    
    # Google News scraping
    if "google_news" in sources:
        try:
            news_results = scrape_google_news(keywords, limit=limit)
            results["google_news"] = news_results
            all_results.extend(news_results)
            logging.info(f"Google News scraping found {len(news_results)} results")
        except Exception as e:
            logging.exception(f"Error in Google News scraping: {e}")
            results["google_news"] = []
    
    # Reddit scraping
    if "reddit" in sources:
        try:
            reddit_results = scrape_reddit_posts(keywords, subreddits=subreddits, limit=limit)
            results["reddit"] = reddit_results
            all_results.extend(reddit_results)
            logging.info(f"Reddit scraping found {len(reddit_results)} results")
        except Exception as e:
            logging.exception(f"Error in Reddit scraping: {e}")
            results["reddit"] = []
    
    # Twitter/X scraping
    if "twitter" in sources:
        try:
            twitter_results = scrape_twitter_posts(keywords, limit=limit)
            results["twitter"] = twitter_results
            all_results.extend(twitter_results)
            logging.info(f"Twitter scraping found {len(twitter_results)} results")
        except Exception as e:
            logging.exception(f"Error in Twitter scraping: {e}")
            results["twitter"] = []
    
    # LinkedIn scraping
    if "linkedin" in sources:
        try:
            linkedin_results = scrape_linkedin_posts(keywords=keywords, post_urls=linkedin_urls, limit=limit)
            results["linkedin"] = linkedin_results
            all_results.extend(linkedin_results)
            logging.info(f"LinkedIn scraping found {len(linkedin_results)} results")
        except Exception as e:
            logging.exception(f"Error in LinkedIn scraping: {e}")
            results["linkedin"] = []
    
    # Save all results to a JSON file
    save_results(all_results)
    
    # Return all the results
    results["all"] = all_results
    return results
