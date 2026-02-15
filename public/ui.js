// Palette: UI Interactions for Better Feedback & Accessibility

/**
 * Handles async button actions with loading states and feedback.
 * @param {HTMLButtonElement} button - The button triggering the action
 * @param {string} url - API endpoint
 * @param {object} options - Fetch options
 */
async function handleButtonAction(button, url, options = {}) {
    const originalText = button.innerText;

    // 0. Auth Check
    let apiKey = localStorage.getItem("voyager_api_key");
    if (!apiKey) {
        apiKey = prompt("Please enter the API Key (default: voyager-secret-123):");
        if (apiKey) {
            localStorage.setItem("voyager_api_key", apiKey);
        } else {
            // User cancelled
            return;
        }
    }

    // Add Header
    const headers = options.headers || {};
    headers["X-API-Key"] = apiKey;
    options.headers = headers;

    // 1. Loading State
    button.disabled = true;
    button.innerText = "Processing...";
    button.setAttribute("aria-busy", "true");
    button.style.cursor = "wait";

    try {
        const response = await fetch(url, options);

        if (!response.ok) {
            if (response.status === 401) {
                localStorage.removeItem("voyager_api_key");
                alert("Invalid or missing API Key. Please try again.");
            }
            throw new Error(`HTTP ${response.status}`);
        }

        // 2. Success State
        button.innerText = "Done!";
        button.style.borderColor = "#66fcf1"; // reinforce success color

        // Refresh telemetry immediately if available
        if (typeof updateTelemetry === 'function') {
            await updateTelemetry();
        }

        // 3. Reset
        setTimeout(() => {
            resetButton(button, originalText);
        }, 1000);

    } catch (error) {
        console.error("Action failed:", error);

        // 4. Error State
        button.innerText = "Error";
        button.style.borderColor = "#ff4d4d";

        setTimeout(() => {
            resetButton(button, originalText);
        }, 2000);
    }
}

/**
 * Handles manual telemetry refresh with feedback.
 * @param {HTMLButtonElement} button
 */
async function handleManualRefresh(button) {
    const originalText = button.innerText;

    button.disabled = true;
    button.innerText = "Fetching...";
    button.setAttribute("aria-busy", "true");

    try {
        if (typeof updateTelemetry === 'function') {
            await updateTelemetry();
            button.innerText = "Updated!";
        } else {
            console.warn("updateTelemetry not found");
        }

        setTimeout(() => {
            resetButton(button, originalText);
        }, 1000);
    } catch (e) {
        button.innerText = "Error";
        setTimeout(() => {
            resetButton(button, originalText);
        }, 2000);
    }
}

function resetButton(button, text) {
    button.innerText = text;
    button.disabled = false;
    button.removeAttribute("aria-busy");
    button.style.cursor = "pointer";
    button.style.borderColor = "";
}
