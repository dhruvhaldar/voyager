// UX: Cache last packet hex to prevent DOM thrashing and text selection loss
let lastPacketHex = null;

async function updateTelemetry() {
    try {
        // SECURITY: Inject API Key if available
        const apiKey = localStorage.getItem('voyager_api_key');
        const headers = apiKey ? { 'X-API-Key': apiKey } : {};

        // OPTIMIZATION: Fetch telemetry and status in parallel to reduce total latency.
        // This is especially beneficial when network RTT is high.
        const [telemetryRes, statusRes] = await Promise.all([
            fetch('/api/telemetry/latest', { headers }),
            fetch('/api/status', { headers })
        ]);

        const [data, status] = await Promise.all([
            telemetryRes.json(),
            statusRes.json()
        ]);

        const hexElement = document.getElementById('packet-hex');
        const detailsElement = document.getElementById('packet-details');

        if (hexElement && detailsElement) {
            // UX: Only update DOM if content has changed (preserves text selection)
            if (data.hex !== lastPacketHex) {
                lastPacketHex = data.hex;

                // Palette: Enable copy button
                const btnCopy = document.getElementById('copy-hex-btn');
                if (btnCopy) btnCopy.disabled = false;

                // Hex string split into bytes
                const bytes = data.hex.split(' ');

                // SECURITY: Use textContent and document.createElement to prevent XSS.
                // Clear existing content
                hexElement.innerHTML = '';

                // OPTIMIZATION: Use DocumentFragment to batch DOM insertions.
                // This prevents N reflows (where N is packet length) and causes only 1 reflow.
                const fragment = document.createDocumentFragment();

                // Reconstruct HTML with classes safely
                bytes.forEach((byte, index) => {
                    const span = document.createElement('span');
                    span.className = 'hex-byte';

                    // Determine type based on index
                    if (index < 6) {
                        span.classList.add('hex-header');
                    } else if (index >= bytes.length - 2) {
                        span.classList.add('hex-crc');
                    } else {
                        span.classList.add('hex-data');
                    }

                    span.textContent = byte;
                    fragment.appendChild(span);
                });

                hexElement.appendChild(fragment);

                // SECURITY: Use textContent and document.createElement to prevent XSS.
                // Clear existing content
                detailsElement.innerHTML = '';

                const detailsFragment = document.createDocumentFragment();

                // Create APID element
                const pApid = document.createElement('p');
                pApid.textContent = 'APID: ';
                const spanApid = document.createElement('span');
                spanApid.className = 'val-highlight';
                spanApid.textContent = '0x' + data.apid.toString(16).toUpperCase();
                pApid.appendChild(spanApid);
                detailsFragment.appendChild(pApid);

                // Create Sequence Count element
                const pSeq = document.createElement('p');
                pSeq.textContent = 'Sequence Count: ';
                const spanSeq = document.createElement('span');
                spanSeq.className = 'val-highlight';
                spanSeq.textContent = data.sequence_count;
                pSeq.appendChild(spanSeq);
                detailsFragment.appendChild(pSeq);

                // Create CRC Valid element
                const pCrc = document.createElement('p');
                pCrc.textContent = 'CRC Valid: ';
                const spanCrc = document.createElement('span');
                if (data.valid_crc) {
                    spanCrc.className = 'status-ok';
                    spanCrc.textContent = 'YES';
                } else {
                    spanCrc.className = 'status-err';
                    spanCrc.textContent = 'NO';
                }
                pCrc.appendChild(spanCrc);
                detailsFragment.appendChild(pCrc);

                detailsElement.appendChild(detailsFragment);
            }

            // Always hide status if we have valid data (idempotent)
            const statusElement = document.getElementById('telemetry-status');
            if (statusElement) statusElement.classList.add('hidden');
        }

        // Update Status Panel
        updateStatusValue('obc-mode', status.mode);
        updateStatusValue('obc-reboots', status.reboot_count);
        document.getElementById('obc-wdt').innerText = status.watchdog_timer.toFixed(1) + 's';

        const commStatus = document.getElementById('comm-status');
        if (commStatus) {
            commStatus.innerText = "LINK ACTIVE";
            commStatus.className = "status-value status-ok";
        }
    } catch (e) {
        console.error("Telemetry update failed:", e);
        const commStatus = document.getElementById('comm-status');
        if (commStatus) {
            commStatus.innerText = "LOS (OFFLINE)";
            commStatus.className = "status-value status-err";
        }

        const statusElement = document.getElementById('telemetry-status');
        if (statusElement) {
            statusElement.classList.remove('hidden');
            statusElement.innerText = "Connection Lost. Retrying...";
            statusElement.className = "status-err";
        }
    }
}

// Global timeout for debouncing copy feedback
let copyTimeout;

function copyHexToClipboard() {
    const hexElement = document.getElementById('packet-hex');
    if (!hexElement) return;

    const text = hexElement.innerText;
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.getElementById('copy-hex-btn');

        // Clear previous timeout to prevent race conditions (e.g. rapid clicks)
        if (copyTimeout) {
            clearTimeout(copyTimeout);
            copyTimeout = null;
        }

        // Store original state on first click
        if (!btn.hasAttribute('data-original-html')) {
            btn.setAttribute('data-original-html', btn.innerHTML);
            btn.setAttribute('data-original-label', btn.getAttribute('aria-label') || "");
        }

        // Update UI & Accessibility
        btn.innerHTML = 'COPIED! <span class="kbd">C</span>';
        btn.style.color = "#66fcf1";
        btn.style.borderColor = "#66fcf1";
        btn.setAttribute('aria-label', "Copied to clipboard");

        // Reset after 2 seconds
        copyTimeout = setTimeout(() => {
            btn.innerHTML = btn.getAttribute('data-original-html');
            const originalLabel = btn.getAttribute('data-original-label');
            if (originalLabel) {
                btn.setAttribute('aria-label', originalLabel);
            } else {
                btn.removeAttribute('aria-label');
            }
            btn.style.color = "";
            btn.style.borderColor = "";
            copyTimeout = null;
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy: ', err);
    });
}

/**
 * Updates a status element and triggers a flash animation if changed.
 * @param {string} elementId - ID of the element
 * @param {string|number} newValue - The new value to display
 */
function updateStatusValue(elementId, newValue) {
    const element = document.getElementById(elementId);
    if (!element) return;

    // Convert to string for comparison
    const strValue = String(newValue);

    if (element.innerText !== strValue) {
        element.innerText = strValue;

        // Remove class if it exists to restart animation
        element.classList.remove('status-changed');

        // Force reflow
        void element.offsetWidth;

        element.classList.add('status-changed');

        // Clean up class after animation (optional, but keeps DOM clean)
        setTimeout(() => {
            element.classList.remove('status-changed');
        }, 500); // Matches CSS duration
    }
}

// Initial fetch
updateTelemetry();
// Poll every 2 seconds
setInterval(updateTelemetry, 2000);
