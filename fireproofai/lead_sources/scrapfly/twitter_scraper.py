"""
Twitter/X Scraper using Scrapfly API for FireproofAI

Scrapes public tweets related to fireproofing and steel construction.
"""
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import quote

from .scrapfly_client import ScrapflyClient
from .utils import normalize_data, log_scraping_result

class TwitterScraper:
    """Twitter/X scraper using Scrapfly API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Twitter scraper.
        
        Args:
            api_key: Optional Scrapfly API key override
        """
        self.client = ScrapflyClient(api_key)
    
    def build_search_url(self, keyword: str) -> str:
        """Build a Twitter search URL for the given keyword.
        
        Args:
            keyword: Keyword to search for
            
        Returns:
            Twitter search URL
        """
        encoded_keyword = quote(keyword)
        return f"https://twitter.com/search?q={encoded_keyword}&src=typed_query&f=live"
    
    def scrape_tweets(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape tweets related to the keyword.
        
        Args:
            keyword: Keyword to search for
            limit: Maximum number of tweets to return
            
        Returns:
            List of normalized tweet data
        """
        url = self.build_search_url(keyword)
        
        try:
            extract_rules = {"tweets": "ai:social_media_post"}
            response = self.client.scrape(
                url=url,
                render_js=True,
                extract_rules=extract_rules,
                wait_for_selector="article[data-testid='tweet']"
            )
            
            if not response.get("success", False):
                error_msg = response.get("error", "Unknown error")
                log_scraping_result("twitter", url, False, error_msg)
                return []
            
            tweets = []
            extracted_data = response.get("result", {}).get("extracted", {}).get("tweets", [])
            
            for tweet_data in extracted_data[:limit]:
                # Extract relevant fields
                tweet_text = tweet_data.get("text", "")
                tweet_title = tweet_data.get("title", "")
                author = tweet_data.get("author", {}).get("name", "")
                tweet_url = tweet_data.get("url", url)
                timestamp = tweet_data.get("date", "")
                
                normalized_tweet = normalize_data(
                    source="twitter",
                    url=tweet_url,
                    title=tweet_title,
                    text=tweet_text,
                    author=author,
                    timestamp=timestamp,
                    raw_data=tweet_data
                )
                
                tweets.append(normalized_tweet)
            
            log_scraping_result("twitter", url, True)
            return tweets
            
        except Exception as e:
            log_scraping_result("twitter", url, False, str(e))
            logging.exception(f"Error scraping Twitter: {e}")
            return []
    
    def scrape_user_timeline(self, username: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape tweets from a specific user's timeline.
        
        Args:
            username: Twitter username (without @)
            limit: Maximum number of tweets to return
            
        Returns:
            List of normalized tweet data
        """
        url = f"https://twitter.com/{username}"
        
        try:
            extract_rules = {"tweets": "ai:social_media_post"}
            response = self.client.scrape(
                url=url,
                render_js=True,
                extract_rules=extract_rules,
                wait_for_selector="article[data-testid='tweet']"
            )
            
            if not response.get("success", False):
                error_msg = response.get("error", "Unknown error")
                log_scraping_result("twitter", url, False, error_msg)
                return []
            
            tweets = []
            extracted_data = response.get("result", {}).get("extracted", {}).get("tweets", [])
            
            for tweet_data in extracted_data[:limit]:
                # Extract relevant fields
                tweet_text = tweet_data.get("text", "")
                tweet_title = tweet_data.get("title", "")
                author = tweet_data.get("author", {}).get("name", "") or username
                tweet_url = tweet_data.get("url", url)
                timestamp = tweet_data.get("date", "")
                
                normalized_tweet = normalize_data(
                    source="twitter",
                    url=tweet_url,
                    title=tweet_title,
                    text=tweet_text,
                    author=author,
                    timestamp=timestamp,
                    raw_data=tweet_data
                )
                
                tweets.append(normalized_tweet)
            
            log_scraping_result("twitter", url, True)
            return tweets
            
        except Exception as e:
            log_scraping_result("twitter", url, False, str(e))
            logging.exception(f"Error scraping Twitter timeline: {e}")
            return []
    
    def scrape_tweet_thread(self, tweet_url: str) -> List[Dict[str, Any]]:
        """Scrape a Twitter thread from a tweet URL.
        
        Args:
            tweet_url: URL of the tweet
            
        Returns:
            List of normalized tweet data from the thread
        """
        try:
            extract_rules = {
                "main_tweet": "ai:social_media_post",
                "replies": "ai:comments"
            }
            response = self.client.scrape(
                url=tweet_url,
                render_js=True,
                extract_rules=extract_rules,
                wait_for_selector="article[data-testid='tweet']"
            )
            
            if not response.get("success", False):
                error_msg = response.get("error", "Unknown error")
                log_scraping_result("twitter", tweet_url, False, error_msg)
                return []
            
            thread_tweets = []
            extracted = response.get("result", {}).get("extracted", {})
            
            # Process the main tweet
            main_tweet = extracted.get("main_tweet", {})
            if main_tweet:
                tweet_text = main_tweet.get("text", "")
                author = main_tweet.get("author", {}).get("name", "")
                timestamp = main_tweet.get("date", "")
                
                normalized_tweet = normalize_data(
                    source="twitter",
                    url=tweet_url,
                    title="",
                    text=tweet_text,
                    author=author,
                    timestamp=timestamp,
                    raw_data=main_tweet
                )
                
                thread_tweets.append(normalized_tweet)
            
            # Process replies
            replies = extracted.get("replies", [])
            for reply in replies:
                reply_text = reply.get("text", "")
                reply_author = reply.get("author", {}).get("name", "")
                reply_timestamp = reply.get("date", "")
                reply_url = reply.get("url", tweet_url)
                
                normalized_reply = normalize_data(
                    source="twitter",
                    url=reply_url,
                    title="",
                    text=reply_text,
                    author=reply_author,
                    timestamp=reply_timestamp,
                    raw_data=reply
                )
                
                thread_tweets.append(normalized_reply)
            
            log_scraping_result("twitter", tweet_url, True)
            return thread_tweets
            
        except Exception as e:
            log_scraping_result("twitter", tweet_url, False, str(e))
            logging.exception(f"Error scraping Twitter thread: {e}")
            return []
