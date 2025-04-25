"""
Test script for Scrapfly-based fireproofing lead scrapers.

Run this script to test individual scrapers or all scrapers together.
"""
import sys
import os
import json
import argparse
from typing import List, Dict, Any
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import scrapers
from scrapfly import (
    scrape_google_news,
    scrape_reddit_posts,
    scrape_twitter_posts,
    scrape_linkedin_posts,
    run_all_scrapers,
    save_results
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default search terms relevant to fireproofing
DEFAULT_KEYWORDS = [
    "steel construction",
    "fireproofing construction",
    "hospital construction", 
    "tower construction", 
    "data center construction",
    "spray applied fireproofing",
    "intumescent coating"
]

# Default subreddits for Reddit search
DEFAULT_SUBREDDITS = ["construction", "architecture", "engineering"]

def display_results(results: List[Dict[str, Any]], limit: int = 1) -> None:
    """
    Display a summary of the results and the first few items.
    
    Args:
        results: List of result items
        limit: Number of items to display in detail
    """
    print(f"\nFound {len(results)} results")
    
    if not results:
        return
    
    # Count results by source
    sources = {}
    states = {}
    project_types = {}
    
    for item in results:
        # Count by source
        source = item.get("source", "unknown")
        sources[source] = sources.get(source, 0) + 1
        
        # Count by state
        state = item.get("state")
        if state:
            states[state] = states.get(state, 0) + 1
            
        # Count by project type
        for project_type in item.get("project_types", []):
            project_types[project_type] = project_types.get(project_type, 0) + 1
    
    # Display counts
    print("\nResults by source:")
    for source, count in sources.items():
        print(f"  - {source}: {count}")
        
    if states:
        print("\nResults by state:")
        for state, count in sorted(states.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {state}: {count}")
            
    if project_types:
        print("\nResults by project type:")
        for project_type, count in sorted(project_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {project_type}: {count}")
    
    # Display detailed information for the first few results
    print(f"\nFirst {min(limit, len(results))} results in detail:")
    for i, item in enumerate(results[:limit]):
        print(f"\n--- Result {i+1} ---")
        print(f"Source: {item.get('source')}")
        print(f"Title: {item.get('title')}")
        print(f"URL: {item.get('url')}")
        print(f"Author: {item.get('author')}")
        if item.get("state"):
            print(f"State: {item.get('state')}")
        if item.get("project_types"):
            print(f"Project Types: {', '.join(item.get('project_types'))}")
        print(f"Summary: {item.get('summary')[:200]}...")

def main():
    """Main function to run the scrapers based on command line arguments."""
    parser = argparse.ArgumentParser(description="Test Scrapfly-based fireproofing lead scrapers")
    
    parser.add_argument(
        "--source", 
        choices=["all", "google_news", "reddit", "twitter", "linkedin"],
        default="all",
        help="Source to scrape (default: all)"
    )
    
    parser.add_argument(
        "--limit", 
        type=int, 
        default=10,
        help="Maximum number of results per source (default: 10)"
    )
    
    parser.add_argument(
        "--display", 
        type=int, 
        default=3,
        help="Number of results to display in detail (default: 3)"
    )
    
    parser.add_argument(
        "--keywords", 
        nargs="+", 
        default=DEFAULT_KEYWORDS,
        help="Keywords to search for (default: predefined fireproofing keywords)"
    )
    
    parser.add_argument(
        "--subreddits", 
        nargs="+", 
        default=DEFAULT_SUBREDDITS,
        help="Subreddits to search in for Reddit (default: construction, architecture, engineering)"
    )
    
    parser.add_argument(
        "--linkedin-urls", 
        nargs="+", 
        default=[],
        help="Specific LinkedIn post URLs to scrape"
    )
    
    parser.add_argument(
        "--output", 
        default="leads.json",
        help="Output filename (default: leads.json)"
    )
    
    args = parser.parse_args()
    
    # Print configuration
    print("\n===== Fireproofing Lead Scraper (Free Tier) =====")
    print(f"Source: {args.source}")
    print(f"Limit per source: {args.limit}")
    print(f"Keywords: {args.keywords}")
    
    if args.source == "reddit" or args.source == "all":
        print(f"Subreddits: {args.subreddits}")
        
    if args.linkedin_urls:
        print(f"LinkedIn URLs: {args.linkedin_urls}")
    
    # Run the scrapers
    results = []
    
    if args.source == "all":
        # Run all scrapers
        print("\nRunning all scrapers...")
        results_dict = run_all_scrapers(
            keywords=args.keywords,
            limit=args.limit,
            subreddits=args.subreddits,
            linkedin_urls=args.linkedin_urls
        )
        results = results_dict["all"]
        
    elif args.source == "google_news":
        # Run Google News scraper
        print("\nRunning Google News scraper...")
        results = scrape_google_news(args.keywords, limit=args.limit)
        
    elif args.source == "reddit":
        # Run Reddit scraper
        print("\nRunning Reddit scraper...")
        results = scrape_reddit_posts(args.keywords, subreddits=args.subreddits, limit=args.limit)
        
    elif args.source == "twitter":
        # Run Twitter scraper
        print("\nRunning Twitter scraper...")
        results = scrape_twitter_posts(args.keywords, limit=args.limit)
        
    elif args.source == "linkedin":
        # Run LinkedIn scraper
        print("\nRunning LinkedIn scraper...")
        results = scrape_linkedin_posts(
            keywords=args.keywords, 
            post_urls=args.linkedin_urls, 
            limit=args.limit
        )
    
    # Display results
    display_results(results, limit=args.display)
    
    # Save results
    output_path = save_results(results, filename=args.output)
    print(f"\nResults saved to: {output_path}")

if __name__ == "__main__":
    main()
