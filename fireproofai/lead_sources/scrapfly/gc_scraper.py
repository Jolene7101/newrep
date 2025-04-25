"""
GC Website Scraper using Scrapfly API for FireproofAI

Scrapes GC (General Contractor) websites like Skanska, Turner, and JE Dunn
to find construction project information.
"""
import logging
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

from .scrapfly_client import ScrapflyClient
from .utils import normalize_data, log_scraping_result

class GCScraper:
    """General Contractor website scraper using Scrapfly API."""
    
    # URLs for popular GC websites
    GC_URLS = {
        "JE Dunn": "https://jedunn.com/projects",
        "Turner": "https://www.turnerconstruction.com/experience",
        "Skanska": "https://www.usa.skanska.com/what-we-deliver/projects/"
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the GC scraper.
        
        Args:
            api_key: Optional Scrapfly API key override
        """
        self.client = ScrapflyClient(api_key)
        self.logger = logging.getLogger(__name__)
    
    def scrape_gc_site(self, gc_name: str) -> List[Dict[str, Any]]:
        """Scrape a specific GC website.
        
        Args:
            gc_name: Name of the GC to scrape ("JE Dunn", "Turner", "Skanska")
            
        Returns:
            List of projects found on the GC website
        """
        if gc_name not in self.GC_URLS:
            self.logger.error(f"Unknown GC name: {gc_name}")
            return []
            
        url = self.GC_URLS[gc_name]
        
        try:
            # Configure scraping parameters specific to GC websites
            params = {
                "url": url,
                "render_js": True,
                "asp": True,  # Help with ASP.NET-based sites
                "ttl": 3600,  # Cache results for an hour
                "tags": f"gc_sites_{gc_name.lower().replace(' ', '_')}",
                "country": "US"
            }
            
            # Add special handling for specific GCs
            if gc_name == "Skanska":
                # Skanska needs more JS rendering time
                params["wait_for_selector"] = ".grid-4"
                params["browser_instructions"] = [
                    {"wait": 3000}  # Wait 3 seconds for JS to load
                ]
                # Use Chrome browser for rendering
                params["browser"] = "chrome"
            
            self.logger.info(f"Scraping {gc_name} website with Scrapfly: {url}")
            response = self.client.scrape(**params)
            
            if not response.get("success", False):
                error_msg = response.get("error", "Unknown error")
                log_scraping_result("gc_sites", url, False, error_msg)
                return []
            
            html = response.get("result", {}).get("content", "")
            
            # Parse the HTML
            soup = BeautifulSoup(html, "html.parser")
            projects = []
            
            # Define selectors based on GC name
            if gc_name == "Skanska":
                selectors = [".item", ".project-card", ".grid-item"]
            elif gc_name == "Turner":
                selectors = [".card", ".project", ".experience-item"]
            elif gc_name == "JE Dunn":
                selectors = [".project", ".card", ".featured-work"]
            else:
                selectors = [".project", ".card", ".item"]
            
            # Find project cards
            for selector in selectors:
                cards = soup.select(selector)
                if cards:
                    self.logger.info(f"Found {len(cards)} project cards using selector '{selector}'")
                    break
            else:
                # If no selectors matched, try generic approach
                cards = soup.find_all(["div", "article"], class_=["project", "card", "item"])
                self.logger.info(f"Found {len(cards)} project cards using generic approach")
            
            # Process found cards
            for card in cards:
                text = card.get_text(strip=True)
                if len(text) > 30:  # Ensure it's substantial content
                    # Try to find a title
                    title_tag = card.find(["h2", "h3", "h4", ".title", ".name"])
                    title = title_tag.get_text(strip=True) if title_tag else text[:50]
                    
                    # Extract location if available (format often like "Location: Denver, CO")
                    location = ""
                    location_tag = card.find(text=lambda t: "location" in t.lower() if t else False)
                    if location_tag:
                        location = location_tag.strip()
                    
                    project = normalize_data(
                        source=f"GC:{gc_name}",
                        url=url,
                        title=title,
                        text=text,
                        author=gc_name,
                        raw_data={"location": location, "html": str(card)[:500]}
                    )
                    projects.append(project)
            
            log_scraping_result("gc_sites", url, True)
            self.logger.info(f"Successfully scraped {len(projects)} projects from {gc_name}")
            return projects
            
        except Exception as e:
            log_scraping_result("gc_sites", url, False, str(e))
            self.logger.exception(f"Error scraping {gc_name} website: {e}")
            return []
    
    def scrape_all_gc_sites(self) -> List[Dict[str, Any]]:
        """Scrape all supported GC websites.
        
        Returns:
            Combined list of projects from all GC websites
        """
        all_projects = []
        for gc_name in self.GC_URLS.keys():
            projects = self.scrape_gc_site(gc_name)
            all_projects.extend(projects)
            
        self.logger.info(f"Scraped a total of {len(all_projects)} projects from all GC sites")
        return all_projects
