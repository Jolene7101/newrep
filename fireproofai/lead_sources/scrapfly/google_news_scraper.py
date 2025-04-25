"""
Google News Scraper using Scrapfly API for FireproofAI

Scrapes Google News articles related to fireproofing and steel construction.
"""
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import quote

from .scrapfly_client import ScrapflyClient
from .utils import normalize_data, log_scraping_result

class GoogleNewsScraper:
    """Google News scraper using Scrapfly API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Google News scraper.
        
        Args:
            api_key: Optional Scrapfly API key override
        """
        self.client = ScrapflyClient(api_key)
    
    def build_search_url(self, keyword: str, time_range: str = None) -> str:
        """Build a Google News search URL for the given keyword.
        
        Args:
            keyword: Keyword to search for
            time_range: Optional time range for results (1h, 1d, 7d, 1m, 1y)
            
        Returns:
            Google News search URL
        """
        encoded_keyword = quote(keyword)
        url = f"https://news.google.com/search?q={encoded_keyword}&hl=en-US&gl=US&ceid=US:en"
        
        if time_range:
            url += f"&when:{time_range}"
            
        return url
    
    def scrape_news(self, keyword: str, limit: int = 20, time_range: str = None) -> List[Dict[str, Any]]:
        """Scrape Google News articles related to the keyword.
        
        Args:
            keyword: Keyword to search for
            limit: Maximum number of articles to return
            time_range: Optional time range for results (1h, 1d, 7d, 1m, 1y)
            
        Returns:
            List of normalized article data
        """
        url = self.build_search_url(keyword, time_range)
        
        try:
            extract_rules = {"articles": "ai:news_article"}
            response = self.client.scrape(
                url=url,
                render_js=True,
                extract_rules=extract_rules,
                wait_for_selector="article"
            )
            
            if not response.get("success", False):
                error_msg = response.get("error", "Unknown error")
                log_scraping_result("google_news", url, False, error_msg)
                return []
            
            articles = []
            extracted_data = response.get("result", {}).get("extracted", {}).get("articles", [])
            
            for article_data in extracted_data[:limit]:
                # Extract relevant fields
                article_text = article_data.get("text", "")
                article_title = article_data.get("title", "")
                source = article_data.get("source", {}).get("name", "")
                article_url = article_data.get("url", "")
                timestamp = article_data.get("date", "")
                
                normalized_article = normalize_data(
                    source="google_news",
                    url=article_url,
                    title=article_title,
                    text=article_text,
                    author=source,  # Use the source name as author
                    timestamp=timestamp,
                    raw_data=article_data
                )
                
                articles.append(normalized_article)
            
            log_scraping_result("google_news", url, True)
            return articles
            
        except Exception as e:
            log_scraping_result("google_news", url, False, str(e))
            logging.exception(f"Error scraping Google News: {e}")
            return []
    
    def scrape_article(self, article_url: str) -> Dict[str, Any]:
        """Scrape a specific news article.
        
        Args:
            article_url: URL of the article to scrape
            
        Returns:
            Normalized article data
        """
        try:
            extract_rules = {"article": "ai:news_article"}
            response = self.client.scrape(
                url=article_url,
                render_js=True,
                extract_rules=extract_rules
            )
            
            if not response.get("success", False):
                error_msg = response.get("error", "Unknown error")
                log_scraping_result("google_news", article_url, False, error_msg)
                return {}
            
            article_data = response.get("result", {}).get("extracted", {}).get("article", {})
            
            # Extract relevant fields
            article_text = article_data.get("text", "")
            article_title = article_data.get("title", "")
            source = article_data.get("source", {}).get("name", "")
            timestamp = article_data.get("date", "")
            
            normalized_article = normalize_data(
                source="google_news",
                url=article_url,
                title=article_title,
                text=article_text,
                author=source,
                timestamp=timestamp,
                raw_data=article_data
            )
            
            log_scraping_result("google_news", article_url, True)
            return normalized_article
            
        except Exception as e:
            log_scraping_result("google_news", article_url, False, str(e))
            logging.exception(f"Error scraping article: {e}")
            return {}
    
    def scrape_topic(self, topic: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape Google News articles from a specific topic section.
        
        Args:
            topic: Topic section (e.g., business, technology, science)
            limit: Maximum number of articles to return
            
        Returns:
            List of normalized article data
        """
        url = f"https://news.google.com/topics/{topic}?hl=en-US&gl=US&ceid=US:en"
        
        try:
            extract_rules = {"articles": "ai:news_article"}
            response = self.client.scrape(
                url=url,
                render_js=True,
                extract_rules=extract_rules,
                wait_for_selector="article"
            )
            
            if not response.get("success", False):
                error_msg = response.get("error", "Unknown error")
                log_scraping_result("google_news", url, False, error_msg)
                return []
            
            articles = []
            extracted_data = response.get("result", {}).get("extracted", {}).get("articles", [])
            
            for article_data in extracted_data[:limit]:
                # Extract relevant fields
                article_text = article_data.get("text", "")
                article_title = article_data.get("title", "")
                source = article_data.get("source", {}).get("name", "")
                article_url = article_data.get("url", "")
                timestamp = article_data.get("date", "")
                
                normalized_article = normalize_data(
                    source="google_news",
                    url=article_url,
                    title=article_title,
                    text=article_text,
                    author=source,
                    timestamp=timestamp,
                    raw_data=article_data
                )
                
                articles.append(normalized_article)
            
            log_scraping_result("google_news", url, True)
            return articles
            
        except Exception as e:
            log_scraping_result("google_news", url, False, str(e))
            logging.exception(f"Error scraping Google News topic: {e}")
            return []
