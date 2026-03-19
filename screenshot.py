from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    # Intercept API calls to force a 401
    page.route("**/api/telemetry/latest", lambda route: route.fulfill(status=401, body="Unauthorized"))
    page.goto('http://localhost:8000')
    time.sleep(2)
    page.screenshot(path='screenshot.png')
    browser.close()
