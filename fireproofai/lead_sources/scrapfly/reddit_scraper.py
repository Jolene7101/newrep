"""
Reddit Scraper using Scrapfly API for FireproofAI

Scrapes Reddit posts and comments related to fireproofing and steel construction.
"""
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import quote

from .scrapfly_client import ScrapflyClient
from .utils import normalize_data, log_scraping_result

class RedditScraper:
    """Reddit scraper using Scrapfly API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Reddit scraper.
        
        Args:
            api_key: Optional Scrapfly API key override
        """
        self.client = ScrapflyClient(api_key)
    
    def build_search_url(self, keyword: str, time_filter: str = "month") -> str:
        """Build a Reddit search URL for the given keyword.
        
        Args:
            keyword: Keyword to search for
            time_filter: Time filter for results (hour, day, week, month, year, all)
            
        Returns:
            Reddit search URL
        """
        encoded_keyword = quote(keyword)
        return f"https://www.reddit.com/search/?q={encoded_keyword}&sort=relevance&t={time_filter}"
    
    def scrape_posts(self, keyword: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Scrape Reddit posts related to the keyword.
        
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
                wait_for_selector=".Post"
            )
            
            if not response.get("success", False):
                error_msg = response.get("error", "Unknown error")
                log_scraping_result("reddit", url, False, error_msg)
                return []
            
            posts = []
            extracted_data = response.get("result", {}).get("extracted", {}).get("posts", [])
            
            for post_data in extracted_data[:limit]:
                # Extract relevant fields
                post_text = post_data.get("text", "")
                post_title = post_data.get("title", "")
                author = post_data.get("author", {}).get("name", "")
                post_url = post_data.get("url", url)
                timestamp = post_data.get("date", "")
                
                normalized_post = normalize_data(
                    source="reddit",
                    url=post_url,
                    title=post_title,
                    text=post_text,
                    author=author,
                    timestamp=timestamp,
                    raw_data=post_data
                )
                
                posts.append(normalized_post)
            
            log_scraping_result("reddit", url, True)
            return posts
            
        except Exception as e:
            log_scraping_result("reddit", url, False, str(e))
            logging.exception(f"Error scraping Reddit: {e}")
            return []
    
    def scrape_thread(self, thread_url: str) -> List[Dict[str, Any]]:
        """Scrape a specific Reddit thread including original post and comments.
        
        Args:
            thread_url: URL of the Reddit thread
            
        Returns:
            List of normalized post and comment data
        """
        try:
            extract_rules = {
                "post": "ai:social_media_post",
                "comments": "ai:comments"
            }
            response = self.client.scrape(
                url=thread_url,
                render_js=True,
                extract_rules=extract_rules,
                wait_for_selector=".Post"
            )
            
            if not response.get("success", False):
                error_msg = response.get("error", "Unknown error")
                log_scraping_result("reddit", thread_url, False, error_msg)
                return []
            
            results = []
            extracted = response.get("result", {}).get("extracted", {})
            
            # Process the main post
            post_data = extracted.get("post", {})
            if post_data:
                post_text = post_data.get("text", "")
                post_title = post_data.get("title", "")
                author = post_data.get("author", {}).get("name", "")
                post_url = post_data.get("url", thread_url)
                timestamp = post_data.get("date", "")
                
                normalized_post = normalize_data(
                    source="reddit",
                    url=post_url,
                    title=post_title,
                    text=post_text,
                    author=author,
                    timestamp=timestamp,
                    raw_data=post_data
                )
                
                results.append(normalized_post)
            
            # Process comments
            comments = extracted.get("comments", [])
            for comment in comments:
                comment_text = comment.get("text", "")
                comment_author = comment.get("author", {}).get("name", "")
                comment_timestamp = comment.get("date", "")
                
                normalized_comment = normalize_data(
                    source="reddit",
                    url=thread_url,
                    title=f"Comment on: {post_title}" if 'post_title' in locals() else "Comment",
                    text=comment_text,
                    author=comment_author,
                    timestamp=comment_timestamp,
                    raw_data=comment
                )
                
                results.append(normalized_comment)
            
            log_scraping_result("reddit", thread_url, True)
            return results
            
        except Exception as e:
            log_scraping_result("reddit", thread_url, False, str(e))
            logging.exception(f"Error scraping Reddit thread: {e}")
            return []
    
    def scrape_subreddit(self, subreddit: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Scrape posts from a specific subreddit.
        
        Args:
            subreddit: Subreddit name (without r/)
            limit: Maximum number of posts to return
            
        Returns:
            List of normalized post data
        """
        url = f"https://www.reddit.com/r/{subreddit}/new/"
        
        try:
            extract_rules = {"posts": "ai:social_media_post"}
            response = self.client.scrape(
                url=url,
                render_js=True,
                extract_rules=extract_rules,
                wait_for_selector=".Post"
            )
            
            if not response.get("success", False):
                error_msg = response.get("error", "Unknown error")
                log_scraping_result("reddit", url, False, error_msg)
                return []
            
            posts = []
            extracted_data = response.get("result", {}).get("extracted", {}).get("posts", [])
            
            for post_data in extracted_data[:limit]:
                # Extract relevant fields
                post_text = post_data.get("text", "")
                post_title = post_data.get("title", "")
                author = post_data.get("author", {}).get("name", "")
                post_url = post_data.get("url", url)
                timestamp = post_data.get("date", "")
                
                normalized_post = normalize_data(
                    source="reddit",
                    url=post_url,
                    title=post_title,
                    text=post_text,
                    author=author,
                    timestamp=timestamp,
                    raw_data=post_data
                )
                
                posts.append(normalized_post)
            
            log_scraping_result("reddit", url, True)
            return posts
            
        except Exception as e:
            log_scraping_result("reddit", url, False, str(e))
            logging.exception(f"Error scraping subreddit: {e}")
            return []
