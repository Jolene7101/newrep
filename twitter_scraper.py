import snscrape.modules.twitter as sntwitter
from typing import List, Dict

def scrape_twitter_posts(keywords: List[str], max_results: int = 20) -> List[Dict]:
    """
    Scrape recent tweets matching any of the given keywords using snscrape.
    Returns a list of dictionaries with tweet info.
    """
    results = []
    for keyword in keywords:
        query = f'{keyword} lang:en'
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
            if i >= max_results:
                break
            results.append({
                'platform': 'Twitter',
                'keyword': keyword,
                'user': tweet.user.username,
                'date': tweet.date.strftime('%Y-%m-%d %H:%M:%S'),
                'content': tweet.content,
                'url': tweet.url
            })
    return results
