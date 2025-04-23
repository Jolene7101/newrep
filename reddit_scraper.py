import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import datetime
from scraper_utils import get_random_user_agent, log_error, log_info

try:
    import praw
except ImportError:
    praw = None

def scrape_reddit_posts(subreddits: List[str], keywords: List[str], max_results: int = 20, proxy: Optional[str] = None, praw_creds: Optional[dict] = None) -> List[Dict]:
    """
    Scrape recent Reddit posts from given subreddits containing any of the keywords.
    Uses praw API if credentials provided, otherwise falls back to static scraping.
    Returns a list of dictionaries with post info.
    """
    results = []
    if praw_creds and praw is not None:
        try:
            reddit = praw.Reddit(
                client_id=praw_creds['client_id'],
                client_secret=praw_creds['client_secret'],
                user_agent=praw_creds.get('user_agent', get_random_user_agent()),
                username=praw_creds.get('username'),
                password=praw_creds.get('password'),
                check_for_async=False
            )
            for subreddit in subreddits:
                for submission in reddit.subreddit(subreddit).new(limit=max_results):
                    title = submission.title
                    if not any(kw.lower() in title.lower() for kw in keywords):
                        continue
                    results.append({
                        'platform': 'Reddit',
                        'subreddit': subreddit,
                        'title': title,
                        'url': f'https://www.reddit.com{submission.permalink}',
                        'scraped_at': datetime.datetime.utcnow().isoformat()
                    })
            log_info('Reddit', f"Scraped {len(results)} posts using praw API.")
            return results
        except Exception as e:
            log_error('Reddit', f"praw API error: {str(e)}")
            # Fall through to static scraping

    headers = {'User-Agent': get_random_user_agent()}
    proxies = {'http': proxy, 'https': proxy} if proxy else None
    for subreddit in subreddits:
        url = f'https://www.reddit.com/r/{subreddit}/new/'
        try:
            resp = requests.get(url, headers=headers, proxies=proxies, timeout=20, verify=not ignore_ssl)
            if resp.status_code != 200:
                log_error('Reddit', f"HTTP {resp.status_code} for {url}")
                continue
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
            log_info('Reddit', f"Scraped {len(posts)} posts from {url} via static scraping.")
        except Exception as e:
            log_error('Reddit', f"{subreddit}: {str(e)}")
    return results
