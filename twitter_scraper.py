import logging
import time
from typing import List, Dict, Any, Optional
import certifi
import os

# Ensure SSL certificates are properly set
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['SSL_CERT_FILE'] = certifi.where()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import Scrapfly integration first
try:
    from fireproofai.lead_sources.scrapfly.twitter_scraper import TwitterScraper
    SCRAPFLY_AVAILABLE = True
    logger.info("Using Scrapfly Twitter integration")
except ImportError:
    SCRAPFLY_AVAILABLE = False
    logger.warning("Scrapfly Twitter integration not available, falling back to snscrape")
    try:
        import snscrape.modules.twitter as sntwitter
    except ImportError:
        logger.error("snscrape module not available - Twitter scraping will not work")


def scrape_twitter_posts(keywords: List[str], max_results: int = 20, retries: int = 3,
                         delay: int = 2) -> List[Dict[str, Any]]:
    """
    Scrape recent tweets matching any of the given keywords.
    Tries Scrapfly first, then falls back to snscrape with retries if needed.
    
    Args:
        keywords: List of keywords to search for
        max_results: Maximum number of results to return per keyword
        retries: Number of retry attempts if scraping fails
        delay: Delay in seconds between retries
        
    Returns:
        List of dictionaries containing tweet data
    """
    all_results = []
    
    # Clean up keywords
    clean_keywords = [k.strip() for k in keywords if k and k.strip()]
    if not clean_keywords:
        logger.warning("No valid keywords provided for Twitter scraping")
        return all_results
    
    # Try with Scrapfly first if available
    if SCRAPFLY_AVAILABLE:
        try:
            logger.info(f"Attempting to scrape Twitter using Scrapfly for keywords: {clean_keywords}")
            scraper = TwitterScraper()
            for keyword in clean_keywords:
                try:
                    scrapfly_results = scraper.scrape_tweets(keyword, limit=max_results)
                    for result in scrapfly_results:
                        # Convert to our standard format
                        all_results.append({
                            'source': 'Twitter',
                            'keyword': keyword,
                            'user': result.get('author', ''),
                            'date': result.get('timestamp', ''),
                            'title': '',  # Twitter doesn't have titles
                            'description': result.get('text', ''),
                            'url': result.get('url', '')
                        })
                    logger.info(f"Successfully scraped {len(scrapfly_results)} tweets for '{keyword}'")
                except Exception as e:
                    logger.error(f"Error scraping Twitter with Scrapfly for keyword '{keyword}': {e}")
            
            if all_results:
                logger.info(f"Scrapfly Twitter scraping successful, found {len(all_results)} tweets")
                return all_results
            logger.warning("Scrapfly Twitter scraping returned no results, falling back to snscrape")
        except Exception as e:
            logger.error(f"Scrapfly Twitter scraping failed, falling back to snscrape: {e}")
    
    # Fall back to snscrape if Scrapfly failed or is not available
    if not all_results and 'sntwitter' in globals():
        for keyword in clean_keywords:
            for attempt in range(retries):
                try:
                    logger.info(f"Attempting to scrape Twitter using snscrape for keyword '{keyword}' (attempt {attempt+1}/{retries})")
                    query = f'{keyword} lang:en'
                    keyword_results = []
                    
                    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
                        if i >= max_results:
                            break
                        keyword_results.append({
                            'source': 'Twitter',
                            'keyword': keyword,
                            'user': tweet.user.username,
                            'date': tweet.date.strftime('%Y-%m-%d %H:%M:%S'),
                            'title': '',  # Twitter doesn't have titles
                            'description': tweet.content,
                            'url': tweet.url
                        })
                    
                    all_results.extend(keyword_results)
                    logger.info(f"Successfully scraped {len(keyword_results)} tweets for '{keyword}'")
                    break  # Break the retry loop on success
                
                except Exception as e:
                    logger.warning(f"Twitter scraping attempt {attempt+1}/{retries} failed for '{keyword}': {e}")
                    if attempt < retries - 1:
                        logger.info(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
                    else:
                        logger.error(f"All retry attempts failed for Twitter scraping '{keyword}'")
    
    logger.info(f"Completed Twitter scraping, found {len(all_results)} results")
    return all_results

