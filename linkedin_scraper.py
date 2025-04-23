import requests
from bs4 import BeautifulSoup
from scraper_utils import get_random_user_agent, log_error, log_info

def scrape_linkedin_posts(keywords):
    # NOTE: This uses public search. For authenticated search, LinkedIn API or session cookies needed.
    query = "+".join(keywords)
    url = f"https://www.linkedin.com/search/results/content/?keywords={query}&origin=SWITCH_SEARCH_VERTICAL"

    headers = {
        "User-Agent": get_random_user_agent()
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            log_error("LinkedIn", f"HTTP {response.status_code} for {url}")
            return []
        if "captcha" in response.text.lower():
            log_error("LinkedIn", "Blocked by CAPTCHA. Consider using session cookies or proxies.")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        posts = []
        for post in soup.find_all("div", class_="base-search-card__info"):
            title = post.get_text(strip=True)
            posts.append({"source": "LinkedIn", "title": title, "description": title})
        log_info("LinkedIn", f"Scraped {len(posts)} posts for keywords: {keywords}")
        return posts
    except Exception as e:
        log_error("LinkedIn", str(e))
        return []