"""
Utility functions for Scrapfly scrapers
"""
import re
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Keywords relevant to fireproofing industry
FIREPROOFING_KEYWORDS = [
    "fireproofing",
    "fire proofing",
    "steel fireproofing",
    "intumescent coating",
    "cementitious fireproofing",
    "spray-applied fireproofing",
    "SFRM",
    "passive fire protection",
    "fire resistant",
    "fire resistance rating",
    "fire retardant"
]

# State abbreviations and full names for location extraction
STATE_PATTERNS = {
    "AL": ["Alabama", r"\bAL\b"],
    "AK": ["Alaska", r"\bAK\b"],
    "AZ": ["Arizona", r"\bAZ\b"],
    "AR": ["Arkansas", r"\bAR\b"],
    "CA": ["California", r"\bCA\b"],
    "CO": ["Colorado", r"\bCO\b"],
    "CT": ["Connecticut", r"\bCT\b"],
    "DE": ["Delaware", r"\bDE\b"],
    "FL": ["Florida", r"\bFL\b"],
    "GA": ["Georgia", r"\bGA\b"],
    "HI": ["Hawaii", r"\bHI\b"],
    "ID": ["Idaho", r"\bID\b"],
    "IL": ["Illinois", r"\bIL\b"],
    "IN": ["Indiana", r"\bIN\b"],
    "IA": ["Iowa", r"\bIA\b"],
    "KS": ["Kansas", r"\bKS\b"],
    "KY": ["Kentucky", r"\bKY\b"],
    "LA": ["Louisiana", r"\bLA\b"],
    "ME": ["Maine", r"\bME\b"],
    "MD": ["Maryland", r"\bMD\b"],
    "MA": ["Massachusetts", r"\bMA\b"],
    "MI": ["Michigan", r"\bMI\b"],
    "MN": ["Minnesota", r"\bMN\b"],
    "MS": ["Mississippi", r"\bMS\b"],
    "MO": ["Missouri", r"\bMO\b"],
    "MT": ["Montana", r"\bMT\b"],
    "NE": ["Nebraska", r"\bNE\b"],
    "NV": ["Nevada", r"\bNV\b"],
    "NH": ["New Hampshire", r"\bNH\b"],
    "NJ": ["New Jersey", r"\bNJ\b"],
    "NM": ["New Mexico", r"\bNM\b"],
    "NY": ["New York", r"\bNY\b"],
    "NC": ["North Carolina", r"\bNC\b"],
    "ND": ["North Dakota", r"\bND\b"],
    "OH": ["Ohio", r"\bOH\b"],
    "OK": ["Oklahoma", r"\bOK\b"],
    "OR": ["Oregon", r"\bOR\b"],
    "PA": ["Pennsylvania", r"\bPA\b"],
    "RI": ["Rhode Island", r"\bRI\b"],
    "SC": ["South Carolina", r"\bSC\b"],
    "SD": ["South Dakota", r"\bSD\b"],
    "TN": ["Tennessee", r"\bTN\b"],
    "TX": ["Texas", r"\bTX\b"],
    "UT": ["Utah", r"\bUT\b"],
    "VT": ["Vermont", r"\bVT\b"],
    "VA": ["Virginia", r"\bVA\b"],
    "WA": ["Washington", r"\bWA\b"],
    "WV": ["West Virginia", r"\bWV\b"],
    "WI": ["Wisconsin", r"\bWI\b"],
    "WY": ["Wyoming", r"\bWY\b"]
}

def extract_state(text: str) -> Optional[str]:
    """
    Extract state information from text content.
    
    Args:
        text: The text to extract state information from
        
    Returns:
        State abbreviation if found, None otherwise
    """
    if not text:
        return None
        
    for abbr, patterns in STATE_PATTERNS.items():
        # Check full state name
        if patterns[0] in text:
            return abbr
            
        # Check abbreviation using regex
        if re.search(patterns[1], text):
            return abbr
            
    return None

def extract_tags(text: str) -> List[str]:
    """
    Extract relevant tags based on content.
    
    Args:
        text: The text to extract tags from
        
    Returns:
        List of extracted tags
    """
    if not text:
        return []
        
    tags = []
    for keyword in FIREPROOFING_KEYWORDS:
        if keyword.lower() in text.lower():
            tags.append(keyword)
            
    return list(set(tags))  # Deduplicate tags

def normalize_data(
    source: str,
    url: str,
    title: Optional[str] = None,
    text: Optional[str] = None,
    author: Optional[str] = None,
    timestamp: Optional[str] = None,
    raw_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Normalize scraped data into a consistent format.
    
    Args:
        source: Source platform (linkedin, twitter, reddit, google_news)
        url: URL of the content
        title: Title of the content
        text: Text content
        author: Author of the content
        timestamp: Timestamp of the content
        raw_data: Raw data for debugging/complete access
        
    Returns:
        Normalized data dictionary
    """
    # Combine title and text for tag extraction
    combined_text = " ".join(filter(None, [title or "", text or ""]))
    
    # Basic normalized structure
    normalized = {
        "source": source,
        "url": url,
        "title": title or "",
        "text": text or "",
        "author": author or "",
        "timestamp": timestamp or datetime.now().isoformat(),
        "tags": extract_tags(combined_text),
        "state": extract_state(combined_text),
        "raw_data": raw_data if raw_data else {}
    }
    
    return normalized

def log_scraping_result(source: str, url: str, success: bool, error: Optional[str] = None):
    """
    Log scraping results for monitoring.
    
    Args:
        source: Source platform
        url: URL that was scraped
        success: Whether scraping was successful
        error: Error message if scraping failed
    """
    if success:
        logging.info(f"Successfully scraped {source}: {url}")
    else:
        logging.error(f"Failed to scrape {source}: {url}. Error: {error}")
