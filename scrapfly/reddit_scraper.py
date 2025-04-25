"""
Reddit Scraper using Scrapfly API (Free Tier Compatible)

Extracts fireproofing-relevant construction posts from Reddit.
"""
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import urllib.parse

from .scrapfly_client import scrapfly_get
from .utils import normalize_data

logger = logging.getLogger(__name__)

def scrape_reddit_posts(
    keywords: List[str], 
    subreddits: List[str] = ["construction", "architecture", "engineering"], 
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Scrape Reddit for posts related to the given keywords.
    
    Args:
        keywords: List of keywords to search for
        subreddits: List of subreddits to search in
        limit: Maximum number of results to return
        
    Returns:
        List of normalized Reddit post data
    """
    all_results = []
    
    for keyword in keywords:
        for subreddit in subreddits:
            # Create search URL for the subreddit
            encoded_query = urllib.parse.quote_plus(keyword)
            url = f"https://www.reddit.com/r/{subreddit}/search/?q={encoded_query}&restrict_sr=1&sr_nsfw=&include_over_18=0"
            
            logger.info(f"Scraping Reddit r/{subreddit} for: {keyword}")
            
            try:
                # Make Scrapfly request
                response = scrapfly_get(
                    url,
                    tags=f"fireproofing_leads_reddit_{subreddit}_{keyword.replace(' ', '_')}",
                    wait_for_selector="div[data-testid='post-container']"
                )
                
                if not response.get("success", False):
                    logger.error(f"Failed to scrape Reddit r/{subreddit} for '{keyword}': {response.get('error')}")
                    continue
                    
                html = response.get("result", {}).get("result", {}).get("content", "")
                
                # Parse HTML response
                soup = BeautifulSoup(html, "html.parser")
                posts = soup.select("div[data-testid='post-container']")
                
                logger.info(f"Found {len(posts)} Reddit posts in r/{subreddit} for '{keyword}'")
                
                for post in posts[:limit]:
                    try:
                        # Extract post details
                        title_elem = post.select_one("h3, [data-testid='post-title']")
                        author_elem = post.select_one("a[data-testid='post_author_link']")
                        content_elem = post.select_one("div[data-testid='post-content']")
                        link_elem = post.select_one("a[data-testid='title-link']")
                        time_elem = post.select_one("span[data-testid='post_timestamp']")
                        
                        if not title_elem:
                            continue
                            
                        title = title_elem.get_text(strip=True)
                        post_url = "https://www.reddit.com" + link_elem.get("href", "") if link_elem else ""
                        author = author_elem.get_text(strip=True) if author_elem else "Unknown"
                        timestamp = time_elem.get_text(strip=True) if time_elem else None
                        
                        # Extract post content
                        content = ""
                        if content_elem:
                            # Try to get post text
                            text_elem = content_elem.select_one("div[data-testid='post-content-text']")
                            if text_elem:
                                content = text_elem.get_text(strip=True)
                                
                        # Use a default summary if content is empty
                        summary = content or f"Reddit post in r/{subreddit} about {keyword}"
                        
                        # Normalize data
                        result = normalize_data(
                            source="reddit",
                            url=post_url,
                            title=title,
                            summary=summary,
                            author=author,
                            timestamp=timestamp,
                            raw_data={
                                "subreddit": subreddit,
                                "keyword": keyword,
                                "html": str(post)[:500]
                            }
                        )
                        
                        all_results.append(result)
                        
                        # Respect the limit
                        if len(all_results) >= limit:
                            break
                            
                    except Exception as e:
                        logger.exception(f"Error processing Reddit post: {e}")
                        continue
                        
            except Exception as e:
                logger.exception(f"Error scraping Reddit r/{subreddit} for '{keyword}': {e}")
                
            # Respect the overall limit
            if len(all_results) >= limit:
                break
                
        # Respect the overall limit across keywords
        if len(all_results) >= limit:
            break
            
    return all_results
