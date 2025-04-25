"""
Utility functions for fireproofing lead scraping.
"""
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from .location import extract_state, detect_project_type

logger = logging.getLogger(__name__)

def normalize_data(
    source: str,
    url: str,
    title: Optional[str] = None,
    summary: Optional[str] = None,
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
        summary: Text content
        author: Author of the content
        timestamp: Timestamp of the content
        raw_data: Raw data for debugging/complete access
        
    Returns:
        Normalized data dictionary
    """
    # Clean and validate inputs
    if not title and not summary:
        logger.warning(f"Missing both title and summary for {url}")
        if raw_data and isinstance(raw_data, dict):
            title = raw_data.get("title", "Untitled")
            summary = raw_data.get("text", raw_data.get("content", "No content"))
    
    # Ensure we have at least some content
    title = title or "Untitled"
    summary = summary or ""
    text_content = f"{title} {summary}"
    
    # Extract state from text content
    state = extract_state(text_content)
    
    # Detect project types (optional enhancement)
    project_types = detect_project_type(text_content)
    
    # Create normalized result
    result = {
        "source": source,
        "url": url,
        "title": title,
        "summary": summary,
        "author": author or "",
        "timestamp": timestamp or datetime.now().isoformat(),
        "state": state,
        "project_types": project_types,
        "raw": raw_data or {}
    }
    
    return result


def save_results(results: List[Dict[str, Any]], filename: str = "leads.json") -> str:
    """
    Save results to a JSON file.
    
    Args:
        results: List of normalized lead data
        filename: Output filename
        
    Returns:
        Path to the saved file
    """
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, filename)
    
    # Add timestamp to each result if not present
    for result in results:
        if not result.get("timestamp"):
            result["timestamp"] = datetime.now().isoformat()
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Saved {len(results)} leads to {output_path}")
    return output_path
