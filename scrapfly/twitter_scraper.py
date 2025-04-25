"""
Twitter/X Scraper using Scrapfly API (Free Tier Compatible)

Extracts fireproofing-relevant construction tweets from Twitter/X.
"""
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import urllib.parse
import re
from datetime import datetime

from .scrapfly_client import scrapfly_get
from .utils import normalize_data

logger = logging.getLogger(__name__)

def scrape_twitter_posts(
    keywords: List[str], 
    limit: int = 10,
    context_terms: List[str] = ["construction", "project"]
) -> List[Dict[str, Any]]:
    """
    Scrape Twitter/X for posts related to the given keywords.
    
    Args:
        keywords: List of keywords to search for
        limit: Maximum number of results to return
        
    Returns:
        List of normalized Twitter post data
    """
    all_results = []
    
    for keyword in keywords:
        # Create search query with configurable context terms
        context_string = " ".join(context_terms) if context_terms else ""
        search_term = f"{keyword} {context_string}".strip()
        encoded_query = urllib.parse.quote_plus(search_term)
        url = f"https://twitter.com/search?q={encoded_query}&src=typed_query&f=live"
        
        logger.info(f"Scraping Twitter for: {search_term}")
        
        try:
            # Make Scrapfly request with AI extraction rule for social media posts
            response = scrapfly_get(
                url,
                extract_rules={"posts": "ai:social_media_post"},
                tags=f"fireproofing_leads_twitter_{keyword.replace(' ', '_')}",
                wait_for_selector="article[data-testid='tweet']"
            )
            
            if not response.get("success", False):
                logger.error(f"Failed to scrape Twitter for '{keyword}': {response.get('error')}")
                continue
                
            result_data = response.get("result", {}).get("result", {})
            
            # Try to use AI extraction if available (from extract_rules)
            extracted_posts = []
            if "posts" in result_data.get("extracted", {}):
                extracted_posts = result_data.get("extracted", {}).get("posts", [])
                logger.info(f"Extracted {len(extracted_posts)} tweets using AI extraction for '{keyword}'")
            
            if extracted_posts:
                # Process AI-extracted posts
                for post in extracted_posts[:limit]:
                    try:
                        author = post.get("author", {}).get("name", "Unknown")
                        content = post.get("content", "")
                        timestamp = post.get("date")
                        post_url = post.get("url", "")
                        
                        # Use the first line/sentence as title
                        title = content.split('\n')[0][:100] if content else f"Tweet about {keyword}"
                        
                        # Normalize data
                        result = normalize_data(
                            source="twitter",
                            url=post_url,
                            title=title,
                            summary=content,
                            author=author,
                            timestamp=timestamp,
                            raw_data={"keyword": keyword, "raw_post": post}
                        )
                        
                        all_results.append(result)
                        
                    except Exception as e:
                        logger.exception(f"Error processing Twitter AI-extracted post: {e}")
                        continue
            else:
                # Fallback to HTML parsing if AI extraction didn't work
                html = result_data.get("content", "")
                soup = BeautifulSoup(html, "html.parser")
                tweets = soup.select("article[data-testid='tweet']")
                
                logger.info(f"Found {len(tweets)} Twitter posts for '{keyword}' via HTML parsing")
                
                for tweet in tweets[:limit]:
                    try:
                        # Extract tweet details
                        author_elem = tweet.select_one("div[data-testid='User-Name'] a")
                        content_elem = tweet.select_one("div[data-testid='tweetText']")
                        time_elem = tweet.select_one("time")
                        
                        if not content_elem:
                            continue
                            
                        content = content_elem.get_text(strip=True)
                        tweet_url = ""
                        
                        # Try to extract tweet URL
                        link_elem = tweet.select_one("a[href*='/status/']")
                        if link_elem and 'href' in link_elem.attrs:
                            href = link_elem['href']
                            if href.startswith('/'):
                                tweet_url = f"https://twitter.com{href}"
                            else:
                                tweet_url = href
                                
                        author = author_elem.get_text(strip=True) if author_elem else "Unknown"
                        timestamp = time_elem.get("datetime") if time_elem else None
                        
                        # Use the first line/sentence as title
                        title = content.split('\n')[0][:100] if content else f"Tweet about {keyword}"
                        
                        # Normalize data
                        result = normalize_data(
                            source="twitter",
                            url=tweet_url,
                            title=title,
                            summary=content,
                            author=author,
                            timestamp=timestamp,
                            raw_data={"keyword": keyword, "html": str(tweet)[:500]}
                        )
                        
                        all_results.append(result)
                        
                    except Exception as e:
                        logger.exception(f"Error processing Twitter post: {e}")
                        continue
                        
            # Respect the limit
            if len(all_results) >= limit:
                break
                    
        except Exception as e:
            logger.exception(f"Error scraping Twitter for '{keyword}': {e}")
            
    return all_results
