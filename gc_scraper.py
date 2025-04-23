import requests
from bs4 import BeautifulSoup

def scrape_gc_site(gc_name):
    urls = {
        "JE Dunn": "https://jedunn.com/projects",
        "Turner": "https://www.turnerconstruction.com/experience",
        "Skanska": "https://www.usa.skanska.com/what-we-deliver/projects/"
    }

    url = urls.get(gc_name)
    if not url:
        return []

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    projects = []

    for card in soup.find_all(["div", "article"], class_=["project", "card", "item"]):
        text = card.get_text(strip=True)
        if len(text) > 30:
            projects.append({
                "source": gc_name,
                "title": text[:50],
                "description": text
            })

    return projects