import requests
import cloudscraper
from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup
from scraper_utils import get_random_user_agent, log_error, log_info
import certifi
import os
import asyncio
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()
os.environ['SSL_CERT_FILE'] = certifi.where()

def scrape_gc_site(gc_name, proxy=None, ignore_ssl=False, mode="auto"):
    """
    Scrapes the specified GC site. Set ignore_ssl=True to skip SSL verification (for self-signed certs).
    mode: 'requests', 'cloudscraper', 'requests-html', or 'auto' (try all)
    """
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
    errors = []
    modes = [mode] if mode != "auto" else ["requests", "cloudscraper", "requests-html"]
    for m in modes:
        try:
            if m == "requests":
                resp = requests.get(url, headers=headers, proxies=proxies, timeout=20, verify=not ignore_ssl)
                if resp.status_code != 200:
                    raise Exception(f"HTTP {resp.status_code}")
                html = resp.text
            elif m == "cloudscraper":
                scraper = cloudscraper.create_scraper()
                # Always use verify=True unless you fully control the certs
                resp = scraper.get(url, headers=headers, proxies=proxies, timeout=20, verify=not ignore_ssl)
                if resp.status_code != 200:
                    raise Exception(f"HTTP {resp.status_code}")
                html = resp.text
            elif m == "requests-html":
                asession = AsyncHTMLSession()
                async def fetch_page():
                    r = await asession.get(url, headers=headers, proxies=proxies, timeout=20, verify=not ignore_ssl)
                    await r.html.arender(timeout=20)
                    return r
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                r = loop.run_until_complete(fetch_page())
                html = r.html.html
            else:
                raise Exception(f"Unknown mode: {m}")
            soup = BeautifulSoup(html, "html.parser")
            projects = []
            for card in soup.find_all(["div", "article"], class_=["project", "card", "item"]):
                text = card.get_text(strip=True)
                if len(text) > 30:
                    projects.append({
                        "source": gc_name,
                        "title": text[:50],
                        "description": text
                    })
            log_info(gc_name, f"Scraped {len(projects)} projects from {url} using {m}")
            return projects
        except Exception as e:
            errors.append(f"{m}: {e}")
            log_error(gc_name, f"{m} mode failed: {e}")
            continue
    log_error(gc_name, f"All scraping modes failed: {' | '.join(errors)}")
    return []
    return []