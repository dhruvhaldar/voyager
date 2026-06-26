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

    # Focus the first hex byte
    page.locator('span.hex-byte').first.focus()
    time.sleep(1)
    page.screenshot(path='screenshot_before.png')

    # Wait a couple of seconds to let the next polling cycle hit and update the UI
    time.sleep(3)
    page.screenshot(path='screenshot_after.png')

    # Verify it still has focus
    has_focus = page.evaluate("document.activeElement === document.querySelector('.hex-byte')")
    print(f"Has focus after update: {has_focus}")

    browser.close()
