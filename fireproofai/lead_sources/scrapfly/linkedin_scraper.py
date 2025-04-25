"""
LinkedIn Scraper using Scrapfly API for FireproofAI

Scrapes LinkedIn posts related to fireproofing and steel construction.
"""
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import quote

from .scrapfly_client import ScrapflyClient
from .utils import normalize_data, log_scraping_result

class LinkedInScraper:
    """LinkedIn scraper using Scrapfly API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the LinkedIn scraper.
        
        Args:
            api_key: Optional Scrapfly API key override
        """
        self.client = ScrapflyClient(api_key)
        
    def build_search_url(self, keyword: str) -> str:
        """Build a LinkedIn search URL for the given keyword.
        
        Args:
            keyword: Keyword to search for
            
        Returns:
            LinkedIn search URL
        """
        encoded_keyword = quote(keyword)
        return f"https://www.linkedin.com/search/results/content/?keywords={encoded_keyword}&origin=GLOBAL_SEARCH_HEADER"
    
    def scrape_posts(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Scrape LinkedIn posts related to the keyword.
        
        Args:
            keyword: Keyword to search for
            limit: Maximum number of posts to return
            
        Returns:
            List of normalized post data
        """
        url = self.build_search_url(keyword)
        
        try:
            extract_rules = {"posts": "ai:social_media_post"}
            response = self.client.scrape(
                url=url,
                render_js=True,
                extract_rules=extract_rules,
                wait_for_selector=".search-results__list"
            )
            
            if not response.get("success", False):
                error_msg = response.get("error", "Unknown error")
                log_scraping_result("linkedin", url, False, error_msg)
                return []
            
            posts = []
            extracted_data = response.get("result", {}).get("extracted", {}).get("posts", [])
            
            for post_data in extracted_data[:limit]:
                # Extract relevant fields from Scrapfly's AI extraction
                post_text = post_data.get("text", "")
                post_title = post_data.get("title", "")
                author = post_data.get("author", {}).get("name", "")
                post_url = post_data.get("url", url)
                timestamp = post_data.get("date", "")
                
                normalized_post = normalize_data(
                    source="linkedin",
                    url=post_url,
                    title=post_title,
                    text=post_text,
                    author=author,
                    timestamp=timestamp,
                    raw_data=post_data
                )
                
                posts.append(normalized_post)
            
            log_scraping_result("linkedin", url, True)
            return posts
            
        except Exception as e:
            log_scraping_result("linkedin", url, False, str(e))
            logging.exception(f"Error scraping LinkedIn: {e}")
            return []
            
    def scrape_profile_posts(self, profile_url: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Scrape posts from a specific LinkedIn profile.
        
        Args:
            profile_url: LinkedIn profile URL
            limit: Maximum number of posts to return
            
        Returns:
            List of normalized post data
        """
        try:
            extract_rules = {"posts": "ai:social_media_post"}
            response = self.client.scrape(
                url=profile_url,
                render_js=True,
                extract_rules=extract_rules,
                wait_for_selector=".ember-view"
            )
            
            if not response.get("success", False):
                error_msg = response.get("error", "Unknown error")
                log_scraping_result("linkedin", profile_url, False, error_msg)
                return []
            
            posts = []
            extracted_data = response.get("result", {}).get("extracted", {}).get("posts", [])
            
            for post_data in extracted_data[:limit]:
                # Extract relevant fields
                post_text = post_data.get("text", "")
                post_title = post_data.get("title", "")
                author = post_data.get("author", {}).get("name", "")
                post_url = post_data.get("url", profile_url)
                timestamp = post_data.get("date", "")
                
                normalized_post = normalize_data(
                    source="linkedin",
                    url=post_url,
                    title=post_title,
                    text=post_text,
                    author=author,
                    timestamp=timestamp,
                    raw_data=post_data
                )
                
                posts.append(normalized_post)
            
            log_scraping_result("linkedin", profile_url, True)
            return posts
            
        except Exception as e:
            log_scraping_result("linkedin", profile_url, False, str(e))
            logging.exception(f"Error scraping LinkedIn profile: {e}")
            return []
