"""
Google News Scraper using Scrapfly API (Free Tier Compatible)

Extracts fireproofing-relevant construction news from Google News.
"""
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import urllib.parse

from .scrapfly_client import scrapfly_get
from .utils import normalize_data

logger = logging.getLogger(__name__)

def scrape_google_news(keywords: List[str], limit: int = 10) -> List[Dict[str, Any]]:
    """
    Scrape Google News for articles related to the given keywords.
    
    Args:
        keywords: List of keywords to search for
        limit: Maximum number of results to return
        
    Returns:
        List of normalized news article data
    """
    all_results = []
    
    for keyword in keywords:
        # Create search query with construction and fireproofing context
        search_term = f"{keyword} construction project"
        encoded_query = urllib.parse.quote_plus(search_term)
        url = f"https://news.google.com/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        logger.info(f"Scraping Google News for: {search_term}")
        
        try:
            # Make Scrapfly request
            response = scrapfly_get(
                url,
                tags=f"fireproofing_leads_google_news_{keyword.replace(' ', '_')}",
                wait_for_selector="article"
            )
            
            if not response.get("success", False):
                logger.error(f"Failed to scrape Google News for '{keyword}': {response.get('error')}")
                continue
                
            html = response.get("result", {}).get("result", {}).get("content", "")
            
            # Parse HTML response
            soup = BeautifulSoup(html, "html.parser")
            articles = soup.select("article")
            
            logger.info(f"Found {len(articles)} Google News articles for '{keyword}'")
            
            for article in articles[:limit]:
                try:
                    # Extract article details
                    title_elem = article.select_one("h3 a, h4 a")
                    time_elem = article.select_one("time")
                    source_elem = article.select_one("div[data-n-tid='9']")
                    
                    if not title_elem:
                        continue
                        
                    title = title_elem.get_text(strip=True)
                    article_url = "https://news.google.com" + title_elem.get("href", "")[1:] if title_elem.get("href", "").startswith(".") else title_elem.get("href", "")
                    timestamp = time_elem.get("datetime") if time_elem else None
                    source = source_elem.get_text(strip=True) if source_elem else "Unknown Source"
                    
                    # Extract summary (might be in different elements based on Google News layout)
                    summary_elem = article.select_one("p, span[data-n-tid='8']")
                    summary = summary_elem.get_text(strip=True) if summary_elem else ""
                    
                    # Normalize data
                    result = normalize_data(
                        source="google_news",
                        url=article_url,
                        title=title,
                        summary=summary,
                        author=source,
                        timestamp=timestamp,
                        raw_data={"keyword": keyword, "html": str(article)[:500]}
                    )
                    
                    all_results.append(result)
                    
                    # Respect the limit
                    if len(all_results) >= limit:
                        break
                        
                except Exception as e:
                    logger.exception(f"Error processing Google News article: {e}")
                    continue
                    
        except Exception as e:
            logger.exception(f"Error scraping Google News for '{keyword}': {e}")
            
    return all_results
