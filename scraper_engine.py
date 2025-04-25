from linkedin_scraper import scrape_linkedin_posts
from gc_scraper import scrape_gc_site
from twitter_scraper import scrape_twitter_posts
from google_news_scraper import scrape_google_news
from reddit_scraper import scrape_reddit_posts
import streamlit as st
import logging
import time
from typing import List, Dict, Any
import certifi
import os

# Ensure SSL certificates are properly set
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['SSL_CERT_FILE'] = certifi.where()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Optionally, set your proxy and praw credentials here or pass from config
PROXY = None  # e.g., 'http://username:password@proxyhost:port'
PRAW_CREDS = None  # e.g., {'client_id': '...', 'client_secret': '...', 'user_agent': '...', ...}

# Check if Scrapfly is available
try:
    from fireproofai.lead_sources.scrapfly.scrapfly_client import ScrapflyClient
    from fireproofai.lead_sources.scrapfly.linkedin_scraper import LinkedInScraper
    from fireproofai.lead_sources.scrapfly.twitter_scraper import TwitterScraper
    from fireproofai.lead_sources.scrapfly.reddit_scraper import RedditScraper
    from fireproofai.lead_sources.scrapfly.google_news_scraper import GoogleNewsScraper
    from fireproofai.lead_sources.scrapfly.gc_scraper import GCScraper
    SCRAPFLY_AVAILABLE = True
    logger.info("Scrapfly integration is available and will be used as primary scraper")
except ImportError as e:
    SCRAPFLY_AVAILABLE = False
    logger.warning(f"Scrapfly integration not available: {e}. Will use direct scrapers instead.")

def get_active_proxy():
    """Get the active proxy configuration, preferring Streamlit session state if available."""
    # Try to get proxy from Streamlit session state if running via UI
    try:
        return st.session_state.get('pipeline_proxy', PROXY)
    except Exception:
        return PROXY

def clean_keywords(keywords_input) -> List[str]:
    """Clean and normalize keyword input."""
    if isinstance(keywords_input, list):
        # Already a list, just clean it
        return [k.strip() for k in keywords_input if k and k.strip()]
    elif isinstance(keywords_input, str):
        # Split string on commas and clean
        return [k.strip() for k in keywords_input.split(',') if k.strip()]
    else:
        # Try to convert to string and split
        try:
            return [k.strip() for k in str(keywords_input).split(',') if k.strip()]
        except:
            logger.error(f"Unable to process keywords: {keywords_input}")
            return []

def normalize_result(result: Dict[str, Any], source: str, keyword: str = "") -> Dict[str, Any]:
    """Normalize results from different scrapers to a common format."""
    # Standard fields that should exist in all results
    normalized = {
        'source': source,
        'keyword': keyword,
        'title': result.get('title', ''),
        'description': result.get('text', result.get('description', result.get('content', ''))),
        'url': result.get('url', ''),
        'user': result.get('author', result.get('user', '')),
        'date': result.get('timestamp', result.get('date', '')),
    }
    return normalized

def run_all_scrapers(user_filters, enabled_sources, creds, proxy_override=None):
    """Run all enabled scrapers with Scrapfly as primary and direct scrapers as fallback."""
    all_projects = []
    proxy = proxy_override if proxy_override else get_active_proxy()
    
    # Safely handle keyword splitting
    keywords = clean_keywords(user_filters.get("keywords", ""))
    
    if not keywords:
        logger.warning("No valid keywords provided for scraping")
        return all_projects
    
    # Try Scrapfly first if available
    if SCRAPFLY_AVAILABLE:
        try:
            logger.info("Attempting to use Scrapfly for all enabled scrapers")
            
            # LinkedIn scraping with Scrapfly
            if enabled_sources.get("linkedin"):
                try:
                    linkedin_scraper = LinkedInScraper()
                    for keyword in keywords:
                        try:
                            logger.info(f"Scraping LinkedIn with Scrapfly for keyword: {keyword}")
                            results = linkedin_scraper.scrape_posts(keyword)
                            logger.info(f"Found {len(results)} LinkedIn results for '{keyword}'")
                            all_projects.extend(results)
                        except Exception as e:
                            logger.error(f"LinkedIn Scrapfly scraping failed for '{keyword}': {e}")
                except Exception as e:
                    logger.error(f"LinkedIn Scrapfly initialization failed: {e}")
            
            # Twitter scraping with Scrapfly
            if enabled_sources.get("twitter"):
                try:
                    twitter_scraper = TwitterScraper()
                    for keyword in keywords:
                        try:
                            logger.info(f"Scraping Twitter with Scrapfly for keyword: {keyword}")
                            results = twitter_scraper.scrape_tweets(keyword)
                            logger.info(f"Found {len(results)} Twitter results for '{keyword}'")
                            all_projects.extend(results)
                        except Exception as e:
                            logger.error(f"Twitter Scrapfly scraping failed for '{keyword}': {e}")
                except Exception as e:
                    logger.error(f"Twitter Scrapfly initialization failed: {e}")
            
            # Reddit scraping with Scrapfly
            if enabled_sources.get("reddit"):
                try:
                    reddit_scraper = RedditScraper()
                    for keyword in keywords:
                        try:
                            logger.info(f"Scraping Reddit with Scrapfly for keyword: {keyword}")
                            results = reddit_scraper.scrape_posts(keyword)
                            logger.info(f"Found {len(results)} Reddit results for '{keyword}'")
                            all_projects.extend(results)
                        except Exception as e:
                            logger.error(f"Reddit Scrapfly scraping failed for '{keyword}': {e}")
                except Exception as e:
                    logger.error(f"Reddit Scrapfly initialization failed: {e}")
            
            # Google News scraping with Scrapfly
            if enabled_sources.get("google_news"):
                try:
                    news_scraper = GoogleNewsScraper()
                    for keyword in keywords:
                        try:
                            logger.info(f"Scraping Google News with Scrapfly for keyword: {keyword}")
                            results = news_scraper.scrape_news(keyword)
                            logger.info(f"Found {len(results)} Google News results for '{keyword}'")
                            all_projects.extend(results)
                        except Exception as e:
                            logger.error(f"Google News Scrapfly scraping failed for '{keyword}': {e}")
                except Exception as e:
                    logger.error(f"Google News Scrapfly initialization failed: {e}")
            
            # GC Sites scraping with Scrapfly
            if enabled_sources.get("gc_sites"):
                try:
                    gc_scraper = GCScraper()
                    for gc_name in ["JE Dunn", "Turner", "Skanska"]:
                        try:
                            logger.info(f"Scraping {gc_name} website with Scrapfly")
                            results = gc_scraper.scrape_gc_site(gc_name)
                            if results:
                                logger.info(f"Found {len(results)} {gc_name} results with Scrapfly")
                                all_projects.extend(results)
                            else:
                                logger.warning(f"No results found for {gc_name} with Scrapfly")
                        except Exception as e:
                            logger.error(f"{gc_name} Scrapfly scraping failed: {str(e)}")
                except Exception as e:
                    logger.error(f"GC Scrapfly initialization failed: {e}")
                    
            # If we got results from Scrapfly, return results
            if all_projects:
                logger.info(f"Scrapfly scraping completed successfully with {len(all_projects)} total results")
                return all_projects
                
        except Exception as e:
            logger.error(f"Error during Scrapfly scraping: {e}")
    
    # Fallback to direct scrapers or handle missing scrapers
    logger.info("Using direct scrapers for remaining sources or as fallback")
    
    # LinkedIn direct scraping
    if enabled_sources.get("linkedin") and (not SCRAPFLY_AVAILABLE or not any(p.get('source') == 'linkedin' for p in all_projects)):
        try:
            linkedin_results = scrape_linkedin_posts(keywords)
            all_projects.extend(linkedin_results)
            logger.info(f"Direct LinkedIn scraping found {len(linkedin_results)} results")
        except Exception as e:
            logger.error(f"Direct LinkedIn scraping failed: {e}")
    
    # GC Sites scraping using direct method as fallback
    if enabled_sources.get("gc_sites") and (not SCRAPFLY_AVAILABLE or not any(p.get('source', '').startswith('GC:') for p in all_projects)):
        for gc_name in ["JE Dunn", "Turner", "Skanska"]:
            try:
                # Try to use safer approaches first with proper user agent and headers
                gc_projects = scrape_gc_site(
                    gc_name, 
                    proxy=proxy, 
                    ignore_ssl=False, 
                    mode="requests"
                )
                
                if not gc_projects:
                    # If requests failed, try cloudscraper with proper SSL settings
                    logger.info(f"Trying cloudscraper mode for {gc_name} with proper SSL")
                    gc_projects = scrape_gc_site(
                        gc_name, 
                        proxy=proxy, 
                        ignore_ssl=False, 
                        mode="cloudscraper"
                    )
                    
                if not gc_projects and gc_name == "Skanska":
                    # Only as last resort for Skanska, try without SSL verification
                    logger.warning(f"Trying last resort mode for {gc_name} without SSL verification")
                    gc_projects = scrape_gc_site(
                        gc_name, 
                        proxy=proxy, 
                        ignore_ssl=True, 
                        mode="cloudscraper"
                    )
                    
                all_projects.extend(gc_projects)
                logger.info(f"GC site scraping for {gc_name} found {len(gc_projects)} results")
            except Exception as e:
                logger.error(f"GC scraping failed for {gc_name}: {str(e)}")
    
    # Twitter direct scraping
    if enabled_sources.get("twitter") and (not SCRAPFLY_AVAILABLE or not any(p.get('source') == 'twitter' for p in all_projects)):
        try:
            twitter_results = scrape_twitter_posts(keywords)
            all_projects.extend(twitter_results)
            logger.info(f"Direct Twitter scraping found {len(twitter_results)} results")
        except Exception as e:
            logger.error(f"Direct Twitter scraping failed: {e}")
    
    # Google News direct scraping
    if enabled_sources.get("google_news") and (not SCRAPFLY_AVAILABLE or not any(p.get('source') == 'google_news' for p in all_projects)):
        try:
            google_news_results = scrape_google_news(keywords, proxy=proxy)
            all_projects.extend(google_news_results)
            logger.info(f"Direct Google News scraping found {len(google_news_results)} results")
        except Exception as e:
            logger.error(f"Direct Google News scraping failed: {e}")
    
    # Reddit direct scraping
    if enabled_sources.get("reddit") and (not SCRAPFLY_AVAILABLE or not any(p.get('source') == 'reddit' for p in all_projects)):
        try:
            subreddits = ["construction", "architecture", "engineering"]
            reddit_results = scrape_reddit_posts(
                subreddits,
                keywords,
                proxy=proxy,
                praw_creds=PRAW_CREDS
            )
            all_projects.extend(reddit_results)
            logger.info(f"Direct Reddit scraping found {len(reddit_results)} results")
        except Exception as e:
            logger.error(f"Direct Reddit scraping failed: {e}")
    
    logger.info(f"All scraping completed with {len(all_projects)} total results")
    return all_projects