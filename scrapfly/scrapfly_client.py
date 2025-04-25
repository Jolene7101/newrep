"""
Scrapfly API Client for Fireproofing Lead Scraper (Free Tier Compatible)

Provides a shared interface for making requests to the Scrapfly API
while respecting free tier limitations.
"""
import os
import json
import logging
from typing import Dict, Any, Optional
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SCRAPFLY_KEY = os.getenv("SCRAPFLY_API_KEY", "scp-live-bbfcca9cd67c4dfb993c7ed2a7419b28")
USER_EMAIL = "blake.mueller@saint-gobain.com"  # User identifier for tracking

if not SCRAPFLY_KEY:
    logging.error("Missing SCRAPFLY_API_KEY in .env file")

logger = logging.getLogger(__name__)


def scrapfly_get(url: str, extract_rules: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
    """
    Make a request to Scrapfly API with free tier compatible parameters.
    
    Args:
        url: The target URL to scrape
        extract_rules: Optional extraction rules (e.g., "ai:social_media_post")
        **kwargs: Additional Scrapfly parameters to override defaults
        
    Returns:
        Dictionary containing the Scrapfly API response
    """
    # Default parameters optimized for free tier
    params = {
        "key": SCRAPFLY_KEY,
        "url": url,
        "render_js": True,  # Enable dynamic page rendering
        "asp": True,        # Auto proxy rotation
        "country": "us",    # Force US-based proxies
        "ttl": 3600,        # Cache identical requests for 1 hour
        "tags": "fireproofing_leads",
        "meta": {"user": USER_EMAIL}  # Add user identifier for tracking
    }
    
    # Add extraction rules if provided
    if extract_rules:
        params["extract_rules"] = extract_rules
    
    # Override defaults with any kwargs
    params.update(kwargs)
    
    try:
        logger.info(f"Making Scrapfly request to: {url}")
        
        # Make request to Scrapfly API
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                "https://api.scrapfly.io/scrape", 
                params=params
            )
            
        if response.status_code != 200:
            logger.error(f"Scrapfly API error: {response.status_code} - {response.text}")
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
            
        data = response.json()
        if not data.get("result"):
            logger.error(f"Scrapfly API returned no result: {data}")
            return {"success": False, "error": "No result in Scrapfly response"}
            
        logger.info(f"Successfully scraped {url} (size: {len(str(data))} bytes)")
        return {"success": True, "result": data}
        
    except Exception as e:
        logger.exception(f"Error during Scrapfly request to {url}: {str(e)}")
        return {"success": False, "error": str(e)}
