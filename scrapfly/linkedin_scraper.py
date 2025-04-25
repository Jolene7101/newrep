"""
LinkedIn Scraper using Scrapfly API (Free Tier Compatible)

Extracts fireproofing-relevant construction posts from LinkedIn.
"""
import logging
from typing import List, Dict, Any, Union
from bs4 import BeautifulSoup
import urllib.parse
import re

from .scrapfly_client import scrapfly_get
from .utils import normalize_data

logger = logging.getLogger(__name__)

def scrape_linkedin_posts(
    keywords: List[str] = None, 
    post_urls: List[str] = None, 
    limit: int = 10,
    context_terms: List[str] = ["construction", "project"]
) -> List[Dict[str, Any]]:
    """
    Scrape LinkedIn for posts related to the given keywords or directly via URLs.
    
    Args:
        keywords: List of keywords to search for on LinkedIn
        post_urls: List of specific LinkedIn post URLs to scrape
        limit: Maximum number of results to return
        
    Returns:
        List of normalized LinkedIn post data
    """
    all_results = []
    
    # Validate inputs - need at least one of keywords or post_urls
    if not keywords and not post_urls:
        logger.error("Either keywords or post_urls must be provided")
        return []
    
    # Initialize empty lists if None
    keywords = keywords or []
    post_urls = post_urls or []
    
    # First process direct post URLs if provided
    if post_urls:
        logger.info(f"Scraping {len(post_urls)} specific LinkedIn posts")
        
        for post_url in post_urls[:limit]:
            try:
                # Clean and validate URL
                if not (post_url.startswith('https://www.linkedin.com/') or 
                        post_url.startswith('https://linkedin.com/')):
                    logger.warning(f"Invalid LinkedIn URL: {post_url}")
                    continue
                
                # Make Scrapfly request with AI extraction for social media post
                response = scrapfly_get(
                    post_url,
                    extract_rules={"post": "ai:social_media_post"},
                    tags="fireproofing_leads_linkedin_direct",
                    wait_for_selector=".feed-shared-update-v2"
                )
                
                if not response.get("success", False):
                    logger.error(f"Failed to scrape LinkedIn post: {post_url}: {response.get('error')}")
                    continue
                    
                result_data = response.get("result", {}).get("result", {})
                
                # Try to use AI extraction if available
                extracted_post = None
                if "post" in result_data.get("extracted", {}):
                    extracted_post = result_data.get("extracted", {}).get("post")
                
                if extracted_post:
                    # Process AI-extracted post
                    author = extracted_post.get("author", {}).get("name", "Unknown")
                    content = extracted_post.get("content", "")
                    timestamp = extracted_post.get("date")
                    
                    # Use the first line/sentence as title
                    title = content.split('\n')[0][:100] if content else "LinkedIn Post"
                    
                    # Normalize data
                    result = normalize_data(
                        source="linkedin",
                        url=post_url,
                        title=title,
                        summary=content,
                        author=author,
                        timestamp=timestamp,
                        raw_data={"direct_url": True, "raw_post": extracted_post}
                    )
                    
                    all_results.append(result)
                else:
                    # Fallback to HTML parsing
                    html = result_data.get("content", "")
                    result = _parse_linkedin_post_html(html, post_url)
                    if result:
                        all_results.append(result)
                    
            except Exception as e:
                logger.exception(f"Error scraping LinkedIn post {post_url}: {e}")
    
    # Then process keyword searches
    for keyword in keywords:
        # Create search query with configurable context terms
        context_string = " ".join(context_terms) if context_terms else ""
        search_term = f"{keyword} {context_string}".strip()
        encoded_query = urllib.parse.quote_plus(search_term)
        url = f"https://www.linkedin.com/search/results/content/?keywords={encoded_query}&origin=GLOBAL_SEARCH_HEADER"
        
        logger.info(f"Scraping LinkedIn for: {search_term}")
        
        try:
            # Make Scrapfly request
            response = scrapfly_get(
                url,
                tags=f"fireproofing_leads_linkedin_{keyword.replace(' ', '_')}",
                wait_for_selector=".feed-shared-update-v2"
            )
            
            if not response.get("success", False):
                logger.error(f"Failed to scrape LinkedIn for '{keyword}': {response.get('error')}")
                continue
                
            html = response.get("result", {}).get("result", {}).get("content", "")
            
            # Parse HTML response
            soup = BeautifulSoup(html, "html.parser")
            posts = soup.select(".feed-shared-update-v2")
            
            logger.info(f"Found {len(posts)} LinkedIn posts for '{keyword}'")
            
            for post in posts[:limit]:
                try:
                    # Get post URL to extract post ID
                    post_link = post.select_one("a.app-aware-link")
                    if not post_link or not post_link.get("href"):
                        continue
                    
                    post_url = post_link.get("href").split('?')[0]  # Remove query parameters
                    
                    # Extract post details from HTML
                    result = _parse_linkedin_post_html(str(post), post_url, keyword)
                    if result:
                        all_results.append(result)
                    
                except Exception as e:
                    logger.exception(f"Error processing LinkedIn post: {e}")
                    continue
                    
            # Respect the limit
            if len(all_results) >= limit:
                break
                
        except Exception as e:
            logger.exception(f"Error scraping LinkedIn for '{keyword}': {e}")
            
    return all_results


def _parse_linkedin_post_html(html: str, post_url: str, keyword: str = None) -> Dict[str, Any]:
    """
    Parse LinkedIn post HTML to extract relevant information.
    
    Args:
        html: HTML content of the LinkedIn post
        post_url: URL of the LinkedIn post
        keyword: Optional keyword used to find this post
        
    Returns:
        Normalized post data dictionary or None if parsing failed
    """
    try:
        soup = BeautifulSoup(html, "html.parser")
        
        # Extract author information
        author_elem = soup.select_one(".feed-shared-actor__name, .update-components-actor__name")
        author = author_elem.get_text(strip=True) if author_elem else "Unknown LinkedIn User"
        
        # Extract post content
        content_elem = soup.select_one(".feed-shared-update-v2__description, .feed-shared-text")
        content = content_elem.get_text(strip=True) if content_elem else ""
        
        # Try to extract timestamp
        time_elem = soup.select_one(".feed-shared-actor__sub-description, .update-components-actor__sub-description time")
        timestamp = time_elem.get("datetime") if time_elem and time_elem.get("datetime") else None
        
        # If no timestamp in datetime attribute, try to get text
        if not timestamp and time_elem:
            timestamp = time_elem.get_text(strip=True)
        
        # Use the first line/sentence as title
        title = content.split('\n')[0][:100] if content else f"LinkedIn Post about {keyword or 'construction'}"
        
        # Normalize data
        return normalize_data(
            source="linkedin",
            url=post_url,
            title=title,
            summary=content,
            author=author,
            timestamp=timestamp,
            raw_data={"keyword": keyword, "html": html[:500]}
        )
    
    except Exception as e:
        logger.exception(f"Error parsing LinkedIn post HTML: {e}")
        return None
