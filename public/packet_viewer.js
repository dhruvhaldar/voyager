async function updateTelemetry() {
    try {
        const res = await fetch('/api/telemetry/latest');
        const data = await res.json();

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
        }

        // Also update status
        const statusRes = await fetch('/api/status');
        const status = await statusRes.json();

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
    }
}

// Initial fetch
updateTelemetry();
// Poll every 2 seconds
setInterval(updateTelemetry, 2000);
