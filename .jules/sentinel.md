## 2025-05-15 - Watchdog Timer Rewind Vulnerability
**Vulnerability:** The simulation's `tick` function accepted negative time deltas (`dt`), allowing an attacker to decrease the watchdog timer and bypass the safe mode reboot mechanism when the system was frozen.
**Learning:** Simulation parameters that affect state accumulation (like timers) must be strictly monotonic. Trusting client-side input for physical properties like "time" can lead to logic bypasses.
**Prevention:**
1. Validated `dt` at the API boundary using Pydantic's `Query(..., ge=0)`.
2. Added a defensive check in the `OnBoardComputer.tick` method to raise `ValueError` for negative inputs.

## 2025-05-24 - Telemetry Inspector XSS
**Vulnerability:** The `packet_viewer.js` script used `innerHTML` to render telemetry data (APID, Sequence Count, Hex Dump) received from the internal API. While the current API returns safe data, this created a potential Cross-Site Scripting (XSS) vulnerability if the backend logic were compromised or if the API response was intercepted and modified.
**Learning:** Even internal APIs should not be trusted blindly when rendering content in the frontend. Using `innerHTML` for dynamic data injection is always risky, regardless of the source.
**Prevention:**
1. Refactored `updateTelemetry` in `public/packet_viewer.js` to use `textContent` and `document.createElement` for safe DOM manipulation.
2. Ensure future frontend components avoid `innerHTML` when displaying data from external sources.
