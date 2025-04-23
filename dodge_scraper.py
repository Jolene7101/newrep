from playwright.sync_api import sync_playwright
import time

def scrape_dodge_projects(email, password):
    projects = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://connect.dodgepipeline.com")
        page.fill('input[type="email"]', email)
        page.click('button:has-text("Next")')
        page.fill('input[type="password"]', password)
        page.click('button:has-text("Sign in")')

        # Wait for dashboard to load
        page.wait_for_selector("text=Saved Searches", timeout=15000)
        page.click("text=Saved Searches")
        page.click("text=FP Bidding")

        time.sleep(5)  # Let project cards load

        cards = page.query_selector_all(".project-card")
        for card in cards:
            title = card.query_selector("h3").inner_text() if card.query_selector("h3") else "Untitled"
            desc = card.inner_text()
            projects.append({"title": title, "description": desc})

        browser.close()
    return projects