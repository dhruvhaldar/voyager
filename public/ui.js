// Palette: UI Interactions for Better Feedback & Accessibility

/**
 * Handles async button actions with loading states and feedback.
 * @param {HTMLButtonElement} button - The button triggering the action
 * @param {string} url - API endpoint
 * @param {object} options - Fetch options
 */
async function handleButtonAction(button, url, options = {}) {
    const originalText = button.innerText;
    // Enhanced: Allow overriding the restore content/label (e.g., for confirmation buttons)
    const originalContent = options.restoreContent || button.innerHTML;
    const originalLabel = options.restoreLabel || button.getAttribute('aria-label');

    // 0. Loading State

    // 1. Loading State
    button.disabled = true;
    button.innerText = "Processing...";
    button.setAttribute("aria-busy", "true");
    button.style.cursor = "wait";

    try {
        // SECURITY: Inject API Key if available
        const apiKey = localStorage.getItem('voyager_api_key');
        if (apiKey) {
            options.headers = options.headers || {};
            options.headers['X-API-Key'] = apiKey;
        }

        let response = await fetch(url, options);

        // SECURITY: Handle Authentication Challenge
        if (response.status === 401) {
            const key = prompt("Authentication Required: Please enter the API Key (check server logs):");
            if (key) {
                localStorage.setItem('voyager_api_key', key);
                // Retry with new key
                options.headers = options.headers || {};
                options.headers['X-API-Key'] = key;
                response = await fetch(url, options);
            }
        }

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        // 2. Success State
        button.innerText = "Done!";
        button.classList.add('status-ok');

        // Refresh telemetry immediately if available
        if (typeof updateTelemetry === 'function') {
            await updateTelemetry();
        }

        // Log action
        addFdirLog('INFO', `Command '${originalText}' sent successfully.`);

        // 3. Reset
        setTimeout(() => {
            resetButton(button, originalContent, originalLabel);
        }, 1000);

    } catch (error) {
        console.error("Action failed:", error);

        // 4. Error State
        button.innerText = "Error";
        button.classList.add('status-err');

        addFdirLog('ERROR', `Command '${originalText}' failed: ${error.message}`);

        setTimeout(() => {
            resetButton(button, originalContent, originalLabel);
        }, 2000);
    }
}

/**
 * Handles manual telemetry refresh with feedback.
 * @param {HTMLButtonElement} button
 */
async function handleManualRefresh(button) {
    const originalContent = button.innerHTML;
    // Note: Manual refresh doesn't currently change aria-label, so passing null is fine.

    button.disabled = true;
    button.innerText = "Fetching...";
    button.setAttribute("aria-busy", "true");

    try {
        if (typeof updateTelemetry === 'function') {
            await updateTelemetry();
            button.innerText = "Updated!";
            addFdirLog('INFO', "Telemetry updated manually.");
        } else {
            console.warn("updateTelemetry not found");
        }

        setTimeout(() => {
            resetButton(button, originalContent);
        }, 1000);
    } catch (e) {
        button.innerText = "Error";
        addFdirLog('ERROR', "Manual refresh failed.");
        setTimeout(() => {
            resetButton(button, originalContent);
        }, 2000);
    }
}

function resetButton(button, content, label = null) {
    button.innerHTML = content;
    if (label !== null) {
        button.setAttribute('aria-label', label);
    }
    button.disabled = false;
    button.removeAttribute("aria-busy");
    button.style.cursor = "pointer";
    button.style.borderColor = "";
}

/**
 * Appends a log entry to the FDIR log container.
 * @param {string} level - INFO, WARN, ERROR
 * @param {string} message - The message to display
 */
function addFdirLog(level, message) {
    const container = document.getElementById('fdir-logs-container');
    if (!container) return;

    const entry = document.createElement('div');
    entry.className = 'log-entry';

    const time = new Date().toLocaleTimeString('en-US', { hour12: false });

    // Level styling
    let levelClass = 'log-info';
    if (level === 'WARN') levelClass = 'log-warn';
    if (level === 'ERROR') levelClass = 'log-err';

    // Create elements safely
    const timeSpan = document.createElement('span');
    timeSpan.className = 'log-time';
    timeSpan.textContent = time;

    const levelSpan = document.createElement('span');
    levelSpan.className = `log-level ${levelClass}`;
    levelSpan.textContent = `[${level}]`;

    const messageSpan = document.createElement('span');
    messageSpan.className = 'log-message';
    messageSpan.textContent = message;

    entry.appendChild(timeSpan);
    entry.appendChild(document.createTextNode(' '));
    entry.appendChild(levelSpan);
    entry.appendChild(document.createTextNode(' '));
    entry.appendChild(messageSpan);

    // Palette: Smart Auto-Scroll
    // Only scroll to bottom if user is already at the bottom (within 10px tolerance)
    const isAtBottom = Math.abs(container.scrollHeight - container.clientHeight - container.scrollTop) < 10;

    container.appendChild(entry);

    if (isAtBottom) {
        container.scrollTop = container.scrollHeight;
    }
}

// Initialize logs
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('fdir-logs-container');
    if (container && container.children.length === 0) {
        addFdirLog('INFO', 'System Normal.');
        addFdirLog('INFO', 'Memory Scrubbing Active.');
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ignore if user is typing in an input
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        if (e.metaKey || e.ctrlKey || e.altKey) return; // Ignore combinations

        switch (e.key.toLowerCase()) {
            case 's':
                document.getElementById('btn-step')?.click();
                break;
            case 'f':
                document.getElementById('btn-freeze')?.click();
                break;
            case 'r':
                document.getElementById('btn-reboot')?.click();
                break;
            case 'c':
                document.getElementById('copy-hex-btn')?.click();
                break;
        }
    });
});

// Security Enhancement: Event Listeners (Replaces inline onclick)
document.addEventListener('DOMContentLoaded', () => {
    // Control Panel Buttons
    const btnStep = document.getElementById('btn-step');
    if (btnStep) {
        btnStep.addEventListener('click', (e) => {
            handleButtonAction(e.currentTarget, '/api/tick?dt=1.0', { method: 'POST' });
        });
    }

    const btnFreeze = document.getElementById('btn-freeze');
    if (btnFreeze) {
        btnFreeze.addEventListener('click', (e) => {
            handleButtonAction(e.currentTarget, '/api/command/freeze', { method: 'POST' });
        });
    }

    const btnReboot = document.getElementById('btn-reboot');
    if (btnReboot) {
        let confirmTimeout;
        btnReboot.addEventListener('click', (e) => {
            const btn = e.currentTarget;

            // Palette: Confirmation Interaction
            if (btn.dataset.state === 'confirm') {
                // CONFIRMED: Execute Action
                clearTimeout(confirmTimeout);
                btn.dataset.state = '';
                btn.classList.remove('status-warn');

                // Retrieve original state
                const restoreHtml = btn.dataset.originalHtml;
                const restoreLabel = btn.dataset.originalLabel;

                // Call API with instructions to restore the ORIGINAL content, not the current "Confirm?" text
                handleButtonAction(btn, '/api/command/reboot', {
                    method: 'POST',
                    restoreContent: restoreHtml,
                    restoreLabel: restoreLabel
                });
            } else {
                // FIRST CLICK: Ask for Confirmation
                e.preventDefault();
                e.stopImmediatePropagation();

                // Store original state
                btn.dataset.originalHtml = btn.innerHTML;
                btn.dataset.originalLabel = btn.getAttribute('aria-label');

                // Set Confirm State
                btn.dataset.state = 'confirm';
                btn.innerHTML = 'Confirm? <span class="kbd">R</span>';
                btn.setAttribute('aria-label', 'Confirm Reboot? Press again to execute.');
                btn.classList.add('status-warn');

                // Auto-revert if not confirmed
                confirmTimeout = setTimeout(() => {
                    btn.dataset.state = '';
                    btn.innerHTML = btn.dataset.originalHtml;
                    btn.setAttribute('aria-label', btn.dataset.originalLabel);
                    btn.classList.remove('status-warn');
                }, 3000);
            }
        });
    }

    // Copy Hex Button
    const btnCopy = document.getElementById('copy-hex-btn');
    if (btnCopy) {
        btnCopy.addEventListener('click', () => {
            if (typeof copyHexToClipboard === 'function') {
                copyHexToClipboard();
            }
        });
    }

    // Fetch Telemetry Button
    const btnFetch = document.getElementById('btn-fetch-telemetry');
    if (btnFetch) {
        btnFetch.addEventListener('click', (e) => {
            handleManualRefresh(e.currentTarget);
        });
    }
});
