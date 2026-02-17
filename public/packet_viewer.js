async function updateTelemetry() {
    try {
        // OPTIMIZATION: Fetch telemetry and status in parallel to reduce total latency.
        // This is especially beneficial when network RTT is high.
        const [telemetryRes, statusRes] = await Promise.all([
            fetch('/api/telemetry/latest'),
            fetch('/api/status')
        ]);

        const [data, status] = await Promise.all([
            telemetryRes.json(),
            statusRes.json()
        ]);

        const hexElement = document.getElementById('packet-hex');
        const detailsElement = document.getElementById('packet-details');

        if (hexElement && detailsElement) {
            // Hex string split into bytes
            const bytes = data.hex.split(' ');

            // Reconstruct HTML with classes
            // Header (6 bytes)
            let header = bytes.slice(0, 6).map(b => `<span class="hex-byte hex-header">${b}</span>`).join('');
            // Data (rest - 2)
            let payload = bytes.slice(6, -2).map(b => `<span class="hex-byte hex-data">${b}</span>`).join('');
            // CRC (last 2)
            let crc = bytes.slice(-2).map(b => `<span class="hex-byte hex-crc">${b}</span>`).join('');

            hexElement.innerHTML = header + payload + crc;

            detailsElement.innerHTML = `
                <p>APID: <span style="color:#66fcf1">0x${data.apid.toString(16).toUpperCase()}</span></p>
                <p>Sequence Count: <span style="color:#66fcf1">${data.sequence_count}</span></p>
                <p>CRC Valid: ${data.valid_crc ? '<span style="color:#45a29e">YES</span>' : '<span style="color:#ff4d4d">NO</span>'}</p>
            `;

            const statusElement = document.getElementById('telemetry-status');
            if (statusElement) statusElement.classList.add('hidden');
        }

        // Update Status Panel
        document.getElementById('obc-mode').innerText = status.mode;
        document.getElementById('obc-reboots').innerText = status.reboot_count;
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

// Initial fetch
updateTelemetry();
// Poll every 2 seconds
setInterval(updateTelemetry, 2000);
