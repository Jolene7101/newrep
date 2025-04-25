"""
Integration adapter to connect Scrapfly lead scraper with the Streamlit UI.

This module bridges the gap between the standalone Scrapfly scrapers and
the existing lead scraping UI application.
"""
import logging
from typing import List, Dict, Any, Optional

# Import the Scrapfly scrapers
from scrapfly import (
    scrape_google_news,
    scrape_reddit_posts, 
    scrape_twitter_posts,
    scrape_linkedin_posts,
    configure_filters
)

# Import the filter engine to process states
from filter_engine import filter_leads

logger = logging.getLogger(__name__)

def get_scrapfly_leads(
    user_filters: Dict[str, Any],
    enabled_sources: Dict[str, bool],
    limit_per_source: int = 20
) -> List[Dict[str, Any]]:
    """
    Get leads using the Scrapfly-based scrapers based on user filters.
    
    Args:
        user_filters: Filters from the UI (including keywords and states)
        enabled_sources: Dict of enabled sources
        limit_per_source: Maximum number of results per source
        
    Returns:
        List of lead data compatible with the UI
    """
    # Extract keywords and states from user filters
    keywords = user_filters.get("keywords", [])
    if isinstance(keywords, str):
        keywords = [k.strip() for k in keywords.split(",") if k.strip()]
    
    states = user_filters.get("states", [])
    if isinstance(states, str):
        states = [s.strip() for s in states.split(",") if s.strip()]
    
    logger.info(f"Getting leads with Scrapfly for keywords: {keywords}, states: {states}")
    
    # Configure filters based on user's state preferences
    if states:
        # If states are provided, we'll create custom state-specific search terms
        state_terms = []
        for state in states:
            if len(state) == 2:  # State abbreviation
                state_terms.append(state)
            else:  # Full state name
                state_terms.append(state)
        
        # Add state terms to all searches
        context_terms = ["construction", "project"] + state_terms
    else:
        context_terms = ["construction", "project"]
    
    # Determine which sources to scrape
    sources = []
    if enabled_sources.get("linkedin", False):
        sources.append("linkedin")
    if enabled_sources.get("twitter", False):
        sources.append("twitter")
    if enabled_sources.get("reddit", False):
        sources.append("reddit")
    if enabled_sources.get("google_news", False):
        sources.append("google_news")
    
    all_results = []
    
    # Scrape each source if enabled
    if "google_news" in sources:
        try:
            news_results = scrape_google_news(
                keywords=keywords, 
                limit=limit_per_source,
                context_terms=context_terms
            )
            all_results.extend(news_results)
            logger.info(f"Found {len(news_results)} Google News results")
        except Exception as e:
            logger.exception(f"Error scraping Google News: {e}")
    
    if "reddit" in sources:
        try:
            reddit_results = scrape_reddit_posts(
                keywords=keywords, 
                limit=limit_per_source,
                context_terms=context_terms
            )
            all_results.extend(reddit_results)
            logger.info(f"Found {len(reddit_results)} Reddit results")
        except Exception as e:
            logger.exception(f"Error scraping Reddit: {e}")
    
    if "twitter" in sources:
        try:
            twitter_results = scrape_twitter_posts(
                keywords=keywords, 
                limit=limit_per_source,
                context_terms=context_terms
            )
            all_results.extend(twitter_results)
            logger.info(f"Found {len(twitter_results)} Twitter results")
        except Exception as e:
            logger.exception(f"Error scraping Twitter: {e}")
    
    if "linkedin" in sources:
        try:
            linkedin_results = scrape_linkedin_posts(
                keywords=keywords, 
                limit=limit_per_source,
                context_terms=context_terms
            )
            all_results.extend(linkedin_results)
            logger.info(f"Found {len(linkedin_results)} LinkedIn results")
        except Exception as e:
            logger.exception(f"Error scraping LinkedIn: {e}")
    
    # Convert Scrapfly results to the format expected by the UI
    ui_compatible_results = []
    
    for result in all_results:
        ui_result = {
            "source": result.get("source", "unknown"),
            "title": result.get("title", ""),
            "description": result.get("summary", ""),
            "url": result.get("url", ""),
            "author": result.get("author", ""),
            "timestamp": result.get("timestamp", ""),
            "state": result.get("state", ""),
            "project_types": result.get("project_types", [])
        }
        ui_compatible_results.append(ui_result)
    
    # Apply any additional filtering based on user filters
    filtered_results = filter_leads(ui_compatible_results, user_filters)
    
    return filtered_results
