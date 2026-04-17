import os
import subprocess
import time
import pytest
from playwright.sync_api import Page, expect
import requests

# Use a specific port for testing
PORT = 8001
URL = f"http://127.0.0.1:{PORT}"

@pytest.fixture(scope="session", autouse=True)
def live_server():
    """Starts a Uvicorn server in a subprocess for the entire test session."""
    env = os.environ.copy()
    # Provide a consistent API key for testing
    env["VOYAGER_API_KEY"] = "test_key_123"

    server_process = subprocess.Popen(
        ["uvicorn", "api.index:app", "--host", "127.0.0.1", "--port", str(PORT)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for the server to be up
    timeout = 10
    start_time = time.time()
    while True:
        try:
            response = requests.get(f"{URL}/api/health", timeout=1)
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            pass
        if time.time() - start_time > timeout:
            server_process.terminate()
            raise RuntimeError("Failed to start server for tests.")
        time.sleep(0.5)

    yield URL

    server_process.terminate()
    server_process.wait()

@pytest.fixture(autouse=True)
def inject_api_key(page: Page):
    """Ensure the page has the test API key in session storage."""
    # We must navigate to the page before we can set localStorage
    page.goto(URL)
    page.evaluate("() => { sessionStorage.setItem('voyager_api_key', 'test_key_123'); }")
    # Reload so scripts pick up the key if they run on load
    page.reload()

def test_page_load(page: Page):
    """Verify that the page loads correctly and elements are visible."""
    # Wait for the heading to appear
    expect(page.locator("h1")).to_have_text("Voyager Avionics Dashboard")

    # Check initial status displays
    expect(page.locator("#obc-mode")).to_be_visible()

    # Check elements in the packet inspector
    expect(page.locator("#heading-packet-inspector")).to_be_visible()
    expect(page.locator("#btn-fetch-telemetry")).to_be_visible()

def test_fetch_packet(page: Page):
    """Test fetching telemetry data."""
    fetch_btn = page.locator("#btn-fetch-telemetry")

    # Click the button and wait for it to process
    fetch_btn.click()

    # Wait for the hex dump to populate. Before fetch, it usually says "Awaiting payload data..."
    # After fetch, we expect to see hexadecimal numbers.
    hex_dump = page.locator("#packet-hex")

    # Wait for some text to change or a specific structure
    # The UI code clears empty-state class or updates inner text.
    expect(hex_dump).not_to_contain_text("Awaiting payload data...")

    # Ensure the button returns to its normal state
    expect(fetch_btn).to_have_text("Fetch Latest Packet T")

def test_control_panel(page: Page):
    """Test Control Panel Buttons (Step, Freeze, Reboot) with their confirmation states."""

    # --- Test Freeze OBC ---
    freeze_btn = page.locator("#btn-freeze")
    expect(freeze_btn).to_have_text("Freeze OBC F")

    # First click sets it to "Confirm? F"
    freeze_btn.click()
    expect(freeze_btn).to_have_text("Confirm? F")

    # Second click executes
    freeze_btn.click()
    expect(freeze_btn).to_have_text("Done!")
    # Allow it time to reset
    expect(freeze_btn).to_have_text("Freeze OBC F", timeout=2000)

    # --- Test Reboot OBC ---
    reboot_btn = page.locator("#btn-reboot")
    expect(reboot_btn).to_have_text("Reboot OBC R")

    # First click sets it to "Confirm? R"
    reboot_btn.click()
    expect(reboot_btn).to_have_text("Confirm? R")

    # Second click executes
    reboot_btn.click()
    expect(reboot_btn).to_have_text("Done!")
    # Allow it time to reset
    expect(reboot_btn).to_have_text("Reboot OBC R", timeout=2000)

    # --- Test Step +1s ---
    step_btn = page.locator("#btn-step")
    expect(step_btn).to_have_text("Step +1s S")

    # Step has no confirm state, executes immediately
    step_btn.click()
    expect(step_btn).to_have_text("Done!")
    # Allow it time to reset
    expect(step_btn).to_have_text("Step +1s S", timeout=2000)
