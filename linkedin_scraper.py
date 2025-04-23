import requests
from bs4 import BeautifulSoup

def scrape_linkedin_posts(keywords):
    # NOTE: This uses public search. For authenticated search, LinkedIn API or session cookies needed.
    query = "+".join(keywords)
    url = f"https://www.linkedin.com/search/results/content/?keywords={query}&origin=SWITCH_SEARCH_VERTICAL"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    if "captcha" in response.text.lower():
        print("Blocked by LinkedIn. Consider rotating user-agents or using session cookies.")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    posts = []

    for post in soup.find_all("div", class_="base-search-card__info"):
        title = post.get_text(strip=True)
        posts.append({"source": "LinkedIn", "title": title, "description": title})

    return posts