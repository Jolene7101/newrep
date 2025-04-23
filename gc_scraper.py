import requests
from bs4 import BeautifulSoup
from scraper_utils import get_random_user_agent, log_error, log_info

def scrape_gc_site(gc_name, proxy=None):
    urls = {
        "JE Dunn": "https://jedunn.com/projects",
        "Turner": "https://www.turnerconstruction.com/experience",
        "Skanska": "https://www.usa.skanska.com/what-we-deliver/projects/"
    }

    url = urls.get(gc_name)
    if not url:
        log_error("GC", f"Unknown GC name: {gc_name}")
        return []

    headers = {"User-Agent": get_random_user_agent()}
    proxies = {"http": proxy, "https": proxy} if proxy else None

    try:
        resp = requests.get(url, headers=headers, proxies=proxies, timeout=20)
        if resp.status_code != 200:
            log_error(gc_name, f"HTTP {resp.status_code} for {url}")
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        projects = []

        for card in soup.find_all(["div", "article"], class_=["project", "card", "item"]):
            text = card.get_text(strip=True)
            if len(text) > 30:
                projects.append({
                    "source": gc_name,
                    "title": text[:50],
                    "description": text
                })

        log_info(gc_name, f"Scraped {len(projects)} projects from {url}")
        return projects
    except Exception as e:
        log_error(gc_name, str(e))
        return []