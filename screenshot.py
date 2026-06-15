import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto('http://localhost:8000')
    time.sleep(2)
    page.locator('#api-key-input').fill('voyager_admin_808')
    page.locator('button:has-text("Submit")').click()
    time.sleep(2)
    # Get the title of the hovered element
    title = page.locator('span.hex-byte').first.get_attribute('title')
    print(f"Tooltip title: {title}")
    page.locator('span.hex-byte').first.hover()
    time.sleep(1)
    page.screenshot(path='screenshot3.png')
    browser.close()
