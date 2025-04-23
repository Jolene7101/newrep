import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import datetime

def scrape_reddit_posts(subreddits: List[str], keywords: List[str], max_results: int = 20) -> List[Dict]:
    """
    Scrape recent Reddit posts from given subreddits containing any of the keywords.
    Returns a list of dictionaries with post info.
    """
    results = []
    headers = {'User-Agent': 'Mozilla/5.0'}
    for subreddit in subreddits:
        url = f'https://www.reddit.com/r/{subreddit}/new/'
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, 'html.parser')
        posts = soup.find_all('div', attrs={'data-testid': 'post-container'})
        for post in posts:
            title_tag = post.find('h3')
            if not title_tag:
                continue
            title = title_tag.text
            if not any(kw.lower() in title.lower() for kw in keywords):
                continue
            link_tag = post.find('a', href=True)
            link = f"https://www.reddit.com{link_tag['href']}" if link_tag else ''
            results.append({
                'platform': 'Reddit',
                'subreddit': subreddit,
                'title': title,
                'url': link,
                'scraped_at': datetime.datetime.utcnow().isoformat()
            })
            if len(results) >= max_results:
                break
    return results
