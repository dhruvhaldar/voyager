async function updateTelemetry() {
    try {
        const res = await fetch('/api/telemetry/latest');
        const data = await res.json();

        const hexElement = document.getElementById('packet-hex');
        const detailsElement = document.getElementById('packet-details');

        if (hexElement && detailsElement) {
            hexElement.innerText = data.hex;
            detailsElement.innerHTML = `
                <p>APID: 0x${data.apid.toString(16).toUpperCase()}</p>
                <p>Sequence Count: ${data.sequence_count}</p>
                <p>CRC Valid: ${data.valid_crc ? '<span style="color:green">YES</span>' : '<span style="color:red">NO</span>'}</p>
            `;
        }

        // Also update status
        const statusRes = await fetch('/api/status');
        const status = await statusRes.json();

        document.getElementById('obc-mode').innerText = status.mode;
        document.getElementById('obc-reboots').innerText = status.reboot_count;
        document.getElementById('obc-wdt').innerText = status.watchdog_timer.toFixed(1) + 's';
    } catch (e) {
        console.error("Telemetry update failed:", e);
    }
}

// Initial fetch
updateTelemetry();
// Poll every 2 seconds
setInterval(updateTelemetry, 2000);
