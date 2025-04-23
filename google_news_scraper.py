import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import datetime

def scrape_google_news(keywords: List[str], max_results: int = 20) -> List[Dict]:
    """
    Scrape Google News search results for any of the given keywords.
    Returns a list of dictionaries with news info.
    """
    results = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    for keyword in keywords:
        url = f'https://news.google.com/search?q={keyword.replace(" ", "+")}&hl=en-US&gl=US&ceid=US:en'
        resp = requests.get(url, headers=headers)
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
    return results
