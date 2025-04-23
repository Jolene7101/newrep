from dodge_scraper import scrape_dodge_projects
from linkedin_scraper import scrape_linkedin_posts
from gc_scraper import scrape_gc_site

def run_all_scrapers(user_filters, enabled_sources, creds):
    all_projects = []

    if enabled_sources.get("dodge"):
        dodge_projects = scrape_dodge_projects(
            creds["DODGE_EMAIL"], creds["DODGE_PASSWORD"]
        )
        all_projects.extend(dodge_projects)

    if enabled_sources.get("linkedin"):
        linkedin_projects = scrape_linkedin_posts(user_filters["keywords"].split(","))
        all_projects.extend(linkedin_projects)

    if enabled_sources.get("gc_sites"):
        for gc_name in ["JE Dunn", "Turner", "Skanska"]:
            gc_projects = scrape_gc_site(gc_name)
            all_projects.extend(gc_projects)

    return all_projects