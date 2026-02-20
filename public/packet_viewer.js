async function updateTelemetry() {
    try {
        // OPTIMIZATION: Fetch telemetry and status in parallel to reduce total latency.
        // This is especially beneficial when network RTT is high.
        // SECURITY: Retrieve API Key and add to headers
        const apiKey = localStorage.getItem("voyager_api_key");
        const headers = apiKey ? { "X-API-Key": apiKey } : {};

        const [telemetryRes, statusRes] = await Promise.all([
            fetch('/api/telemetry/latest', { headers }),
            fetch('/api/status', { headers })
        ]);

        // SECURITY: Handle Authentication Failure
        if (telemetryRes.status === 401 || statusRes.status === 401) {
            const statusElement = document.getElementById('telemetry-status');
            if (statusElement) {
                statusElement.classList.remove('hidden');
                statusElement.innerText = "Auth Required (Click a Command)";
                statusElement.style.color = "#ffcc00";
            }
            return;
        }

        const [data, status] = await Promise.all([
            telemetryRes.json(),
            statusRes.json()
        ]);

        const hexElement = document.getElementById('packet-hex');
        const detailsElement = document.getElementById('packet-details');

        if (hexElement && detailsElement) {
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
            spanApid.style.color = '#66fcf1';
            spanApid.textContent = '0x' + data.apid.toString(16).toUpperCase();
            pApid.appendChild(spanApid);
            detailsFragment.appendChild(pApid);

            // Create Sequence Count element
            const pSeq = document.createElement('p');
            pSeq.textContent = 'Sequence Count: ';
            const spanSeq = document.createElement('span');
            spanSeq.style.color = '#66fcf1';
            spanSeq.textContent = data.sequence_count;
            pSeq.appendChild(spanSeq);
            detailsFragment.appendChild(pSeq);

            // Create CRC Valid element
            const pCrc = document.createElement('p');
            pCrc.textContent = 'CRC Valid: ';
            const spanCrc = document.createElement('span');
            if (data.valid_crc) {
                spanCrc.style.color = '#45a29e';
                spanCrc.textContent = 'YES';
            } else {
                spanCrc.style.color = '#ff4d4d';
                spanCrc.textContent = 'NO';
            }
            pCrc.appendChild(spanCrc);
            detailsFragment.appendChild(pCrc);

            detailsElement.appendChild(detailsFragment);

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
            statusElement.style.color = "#ff4d4d";
        }
    }
}

function copyHexToClipboard() {
    const hexElement = document.getElementById('packet-hex');
    if (!hexElement) return;

    const text = hexElement.innerText;
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.getElementById('copy-hex-btn');
        const originalText = btn.innerText;
        btn.innerText = "COPIED!";
        btn.style.color = "#66fcf1";
        btn.style.borderColor = "#66fcf1";

        setTimeout(() => {
            btn.innerText = originalText;
            btn.style.color = "";
            btn.style.borderColor = "";
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
