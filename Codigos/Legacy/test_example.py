import re
from playwright.sync_api import sync_playwright, Page, expect

def test_has_title():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Hace visible el navegador
        page = browser.new_page()
        page.goto("https://playwright.dev/")
        
        # Expect a title "to contain" a substring.
        expect(page).to_have_title(re.compile("Playwright"))
        
        browser.close()

def test_get_started_link():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Hace visible el navegador
        page = browser.new_page()
        page.goto("https://playwright.dev/")

        # Click the "Get started" link.
        page.get_by_role("link", name="Get started").click()

        # Expects page to have a heading with the name "Installation".
        expect(page.get_by_role("heading", name="Installation")).to_be_visible()
        
        browser.close()

