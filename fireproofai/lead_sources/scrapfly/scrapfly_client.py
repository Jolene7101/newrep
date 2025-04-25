"""
Scrapfly API Client for FireproofAI Lead Generation

Provides shared functionality for interacting with the Scrapfly API
across all scraper modules.
"""
import os
import json
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()
SCRAPFLY_KEY = os.getenv("SCRAPFLY_API_KEY")

if not SCRAPFLY_KEY:
    logging.error("Missing SCRAPFLY_API_KEY in .env file")

class ScrapflyClient:
    """Client for interacting with the Scrapfly API."""
    
    BASE_URL = "https://api.scrapfly.io/scrape"
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Scrapfly client.
        
        Args:
            api_key: Optional API key override. If not provided, uses SCRAPFLY_API_KEY from .env
        """
        self.api_key = api_key or SCRAPFLY_KEY
        if not self.api_key:
            raise ValueError("Scrapfly API key is required. Set SCRAPFLY_API_KEY in .env file.")
    
    def scrape(self, 
               url: str,
               render_js: bool = True,
               extract_rules: Optional[Dict[str, str]] = None,
               country_code: Optional[str] = None,
               wait_for_selector: Optional[str] = None,
               proxy_pool: Optional[str] = None,
               retry_attempts: int = 3) -> Dict[str, Any]:
        """Send a scrape request to Scrapfly API.
        
        Args:
            url: Target URL to scrape
            render_js: Whether to render JavaScript
            extract_rules: Scrapfly AI extraction rules
            country_code: Country code for geo-specific scraping
            wait_for_selector: CSS selector to wait for before returning
            proxy_pool: Proxy pool to use (e.g., "public" or "private")
            retry_attempts: Number of retry attempts
            
        Returns:
            Dict containing the scraped data
        """
        params = {
            "key": self.api_key,
            "url": url,
            "render_js": render_js,
            "retry_attempts": retry_attempts,
        }
        
        # Add optional parameters if they are provided
        if extract_rules:
            params["extract_rules"] = extract_rules
        if country_code:
            params["country"] = country_code
        if wait_for_selector:
            params["wait_for_selector"] = wait_for_selector
        if proxy_pool:
            params["proxy_pool"] = proxy_pool
            
        try:
            response = requests.post(self.BASE_URL, json=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Scrapfly API request failed: {e}")
            return {"success": False, "error": str(e)}
