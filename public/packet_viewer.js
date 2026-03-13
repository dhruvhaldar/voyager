// UX: Cache last packet hex to prevent DOM thrashing and text selection loss
let lastPacketHex = null;

async function updateTelemetry() {
    try {
        // SECURITY: Inject API Key if available
        const apiKey = localStorage.getItem('voyager_api_key');
        const headers = apiKey ? { 'X-API-Key': apiKey } : {};

        // OPTIMIZATION: Fetch telemetry and status in a single batched API call to reduce total latency.
        // This avoids making two separate requests, which is especially beneficial when network RTT is high.
        const telemetryRes = await fetch('/api/telemetry/latest', { headers });

        const data = await telemetryRes.json();
        const status = data.status;

        const hexElement = document.getElementById('packet-hex');
        const detailsElement = document.getElementById('packet-details');

        if (hexElement && detailsElement) {
            // UX: Only update DOM if content has changed (preserves text selection)
            if (data.hex !== lastPacketHex) {
                lastPacketHex = data.hex;

                // Palette: Enable copy button
                const btnCopy = document.getElementById('copy-hex-btn');
                if (btnCopy) {
                    btnCopy.disabled = false;
                    btnCopy.setAttribute('title', 'Copy hex dump to clipboard');
                }

                // Hex string split into bytes
                const bytes = data.hex.split(' ');

                // SECURITY: Use textContent and document.createElement to prevent XSS.
                // Clear existing content
                hexElement.textContent = '';

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
                        span.title = 'Primary Header';
                    } else if (index >= bytes.length - 2) {
                        span.classList.add('hex-crc');
                        span.title = 'Packet Error Control (CRC)';
                    } else {
                        span.classList.add('hex-data');
                        span.title = 'Payload Data';
                    }

                    span.textContent = byte;
                    fragment.appendChild(span);
                });

                hexElement.appendChild(fragment);

                // SECURITY: Use textContent and document.createElement to prevent XSS.
                // Clear existing content
                detailsElement.textContent = '';

                const detailsFragment = document.createDocumentFragment();

                // Create APID element
                const pApid = document.createElement('p');
                                const abbrApid = document.createElement('abbr');
                abbrApid.title = 'Application Process Identifier';
                abbrApid.tabIndex = 0;
                abbrApid.textContent = 'APID';
                pApid.appendChild(abbrApid);
                pApid.appendChild(document.createTextNode(': '));
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
                                const abbrCrc = document.createElement('abbr');
                abbrCrc.title = 'Cyclic Redundancy Check';
                abbrCrc.tabIndex = 0;
                abbrCrc.textContent = 'CRC';
                pCrc.appendChild(abbrCrc);
                pCrc.appendChild(document.createTextNode(' Valid: '));
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
            commStatus.classList.remove('status-err');
            commStatus.classList.add('status-ok');
        }
    } catch (e) {
        console.error("Telemetry update failed:", e);
        const commStatus = document.getElementById('comm-status');
        if (commStatus) {
            commStatus.textContent = '';
            const abbrLos = document.createElement('abbr');
            abbrLos.title = "Loss Of Signal";
            abbrLos.tabIndex = 0;
            abbrLos.textContent = "LOS";
            commStatus.appendChild(abbrLos);
            commStatus.appendChild(document.createTextNode(" (OFFLINE)"));
            commStatus.classList.remove('status-ok');
            commStatus.classList.add('status-err');
        }

        const statusElement = document.getElementById('telemetry-status');
        if (statusElement) {
            statusElement.classList.remove('hidden');
            statusElement.innerText = "Connection Lost. Retrying...";
            statusElement.classList.add('status-err');
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
        if (!btn.__originalNodes) {
            btn.__originalNodes = Array.from(btn.childNodes).map(n => n.cloneNode(true));
            btn.setAttribute('data-original-label', btn.getAttribute('aria-label') || "");
        }

        // Update UI & Accessibility safely
        btn.textContent = 'COPIED! ';
        const kbdSpan = document.createElement('span');
        kbdSpan.className = 'kbd';
        kbdSpan.textContent = 'C';
        btn.appendChild(kbdSpan);

        btn.style.color = "#66fcf1";
        btn.style.borderColor = "#66fcf1";
        btn.setAttribute('aria-label', "Copied to clipboard");

        // Reset after 2 seconds
        copyTimeout = setTimeout(() => {
            btn.textContent = '';
            btn.__originalNodes.forEach(node => btn.appendChild(node.cloneNode(true)));

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
