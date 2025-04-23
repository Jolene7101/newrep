import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import datetime
from scraper_utils import get_random_user_agent, log_error, log_info

def scrape_google_news(keywords: List[str], max_results: int = 20, proxy=None) -> List[Dict]:
    """
    Scrape Google News search results for any of the given keywords.
    Returns a list of dictionaries with news info.
    """
    results = []
    headers = {'User-Agent': get_random_user_agent()}
    proxies = {'http': proxy, 'https': proxy} if proxy else None
    for keyword in keywords:
        url = f'https://news.google.com/search?q={keyword.replace(" ", "+")}&hl=en-US&gl=US&ceid=US:en'
        try:
            resp = requests.get(url, headers=headers, proxies=proxies, timeout=20)
            if resp.status_code != 200:
                log_error("GoogleNews", f"HTTP {resp.status_code} for {url}")
                continue
            soup = BeautifulSoup(resp.text, 'html.parser')
            articles = soup.select('article')
            for i, article in enumerate(articles):
                if i >= max_results:
                    break
                title_tag = article.find('h3') or article.find('h4')
                title = title_tag.text if title_tag else 'No title'
                link_tag = article.find('a', href=True)
                link = f"https://news.google.com{link_tag['href'][1:]}" if link_tag else ''
                results.append({
                    'platform': 'Google News',
                    'keyword': keyword,
                    'title': title,
                    'url': link,
                    'scraped_at': datetime.datetime.utcnow().isoformat()
                })
            log_info("GoogleNews", f"Scraped {len(articles)} articles for keyword: {keyword}")
        except Exception as e:
            log_error("GoogleNews", f"{keyword}: {str(e)}")
    return results
