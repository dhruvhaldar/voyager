from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto("http://localhost:8000")
        page.wait_for_timeout(1000)

        # Step simulation to generate some data
        page.get_by_role("button", name="Step simulation forward 1 second").click()
        page.wait_for_timeout(1000)

        # Take screenshot of populated state
        page.screenshot(path="screenshot2.png")
        browser.close()

if __name__ == "__main__":
    run()