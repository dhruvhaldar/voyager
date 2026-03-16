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
    // To avoid innerHTML, we store an array of cloned child nodes
    const originalContent = options.restoreNodes || Array.from(button.childNodes).map(n => n.cloneNode(true));
    const originalLabel = options.restoreLabel || button.getAttribute('aria-label');

    // 0. Loading State

    // 1. Loading State
    button.disabled = true;
    button.title = "Action in progress, please wait";
    button.innerText = "Processing...";
    button.setAttribute("aria-label", "Processing...");
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
        button.setAttribute("aria-label", "Done!");
        button.classList.add('status-ok');
        button.removeAttribute('aria-busy');
        button.removeAttribute('title');

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
        button.setAttribute("aria-label", "Error");
        button.classList.add('status-err');
        button.removeAttribute('aria-busy');
        button.title = "Action failed";

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
    const originalContent = Array.from(button.childNodes).map(n => n.cloneNode(true));
    const originalLabel = button.getAttribute('aria-label');

    button.disabled = true;
    button.title = "Fetching latest telemetry, please wait";
    button.innerText = "Fetching...";
    button.setAttribute("aria-label", "Fetching...");
    button.setAttribute("aria-busy", "true");

    try {
        if (typeof updateTelemetry === 'function') {
            await updateTelemetry();
            button.innerText = "Updated!";
            button.setAttribute("aria-label", "Updated!");
            button.removeAttribute('aria-busy');
            button.removeAttribute('title');
            addFdirLog('INFO', "Telemetry updated manually.");
        } else {
            console.warn("updateTelemetry not found");
        }

        setTimeout(() => {
            resetButton(button, originalContent, originalLabel);
        }, 1000);
    } catch (e) {
        button.innerText = "Error";
        button.setAttribute("aria-label", "Error");
        button.removeAttribute('aria-busy');
        button.title = "Action failed";
        addFdirLog('ERROR', "Manual refresh failed.");
        setTimeout(() => {
            resetButton(button, originalContent, originalLabel);
        }, 2000);
    }
}

function resetButton(button, content, label = null) {
    // If content is an object (Node), we append it, else we set textContent
    button.textContent = ''; // clear
    if (content instanceof DocumentFragment) {
        button.appendChild(content.cloneNode(true)); // clone so it can be reused
    } else if (content instanceof Node) {
        button.appendChild(content.cloneNode(true));
    } else if (Array.isArray(content)) {
        content.forEach(node => button.appendChild(node.cloneNode(true)));
    } else {
        button.textContent = content; // fallback for plain text
    }

    if (label !== null) {
        button.setAttribute('aria-label', label);
    } else {
        button.removeAttribute('aria-label');
    }
    button.disabled = false;
    button.removeAttribute("aria-busy");
    button.removeAttribute("title");
    button.style.cursor = "";
    button.style.borderColor = "";
    button.classList.remove('status-ok', 'status-err', 'status-warn');
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
            case 't':
                document.getElementById('btn-fetch-telemetry')?.click();
                break;
        }
    });
});


/**
 * Sets up a two-step confirmation interaction for destructive actions.
 * @param {string} btnId - The ID of the button
 * @param {string} apiUrl - The API endpoint to call
 * @param {string} kbdShortcut - The keyboard shortcut letter to display
 * @param {string} ariaLabel - The ARIA label for the confirmation state
 */
function setupConfirmAction(btnId, apiUrl, kbdShortcut, ariaLabel) {
    const btn = document.getElementById(btnId);
    if (!btn) return;

    let confirmTimeout;
    btn.addEventListener('click', (e) => {
        const targetBtn = e.currentTarget;

        // Palette: Confirmation Interaction
        if (targetBtn.dataset.state === 'confirm') {
            // CONFIRMED: Execute Action
            clearTimeout(confirmTimeout);
            targetBtn.dataset.state = '';
            targetBtn.classList.remove('status-warn');

            // Retrieve original state
            const restoreNodes = targetBtn.__originalNodes || [];
            const restoreLabel = targetBtn.dataset.originalLabel;

            // Call API with instructions to restore the ORIGINAL content
            handleButtonAction(targetBtn, apiUrl, {
                method: 'POST',
                restoreNodes: restoreNodes,
                restoreLabel: restoreLabel
            });
        } else {
            // FIRST CLICK: Ask for Confirmation
            e.preventDefault();
            e.stopImmediatePropagation();

            // Store original state using actual Nodes to avoid innerHTML
            targetBtn.__originalNodes = Array.from(targetBtn.childNodes).map(n => n.cloneNode(true));
            targetBtn.dataset.originalLabel = targetBtn.getAttribute('aria-label');

            // Set Confirm State safely
            targetBtn.dataset.state = 'confirm';
            targetBtn.textContent = 'Confirm? ';
            const kbdSpan = document.createElement('span');
            kbdSpan.className = 'kbd';
            kbdSpan.textContent = kbdShortcut;
            targetBtn.appendChild(kbdSpan);

            targetBtn.setAttribute('aria-label', ariaLabel);
            targetBtn.classList.add('status-warn');

            // Auto-revert if not confirmed
            confirmTimeout = setTimeout(() => {
                targetBtn.dataset.state = '';

                // Restore safely
                targetBtn.textContent = '';
                targetBtn.__originalNodes.forEach(node => targetBtn.appendChild(node.cloneNode(true)));

                targetBtn.setAttribute('aria-label', targetBtn.dataset.originalLabel);
                targetBtn.classList.remove('status-warn');
            }, 3000);
        }
    });
}

// Security Enhancement: Event Listeners (Replaces inline onclick)
document.addEventListener('DOMContentLoaded', () => {
    // Control Panel Buttons
    const btnStep = document.getElementById('btn-step');
    if (btnStep) {
        btnStep.addEventListener('click', (e) => {
            handleButtonAction(e.currentTarget, '/api/tick?dt=1.0', { method: 'POST' });
        });
    }

    setupConfirmAction('btn-freeze', '/api/command/freeze', 'F', 'Confirm Freeze? Press again to execute.');
    setupConfirmAction('btn-reboot', '/api/command/reboot', 'R', 'Confirm Reboot? Press again to execute.');

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
