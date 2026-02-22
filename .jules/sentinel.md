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

## 2026-02-19 - Unauthenticated Telemetry Exposure
**Vulnerability:** The `/api/status` and `/api/telemetry/latest` endpoints were accessible without authentication, exposing critical satellite state (OBC mode, watchdog timer) and raw telemetry data to any network observer.
**Learning:** Developers often assume "read-only" data is non-sensitive or that internal APIs are hidden. However, information disclosure can aid attackers in reconnaissance (e.g., monitoring watchdog timers to time an attack).
**Prevention:**
1. Applied `Depends(verify_api_key)` to all API endpoints, including GET requests.
2. Updated frontend `fetch` logic to include `X-API-Key` headers for background polling.

## 2026-05-25 - Content Security Policy Constraints
**Vulnerability:** The application was vulnerable to XSS and clickjacking due to missing HTTP security headers.
**Learning:** Implementing a strict CSP was blocked by the use of inline event handlers (e.g., `onclick="..."`) in the vanilla JS frontend. Refactoring to `addEventListener` was out of scope for a quick fix.
**Prevention:**
1. Implemented a transitional CSP allowing `'unsafe-inline'` for scripts and styles.
2. Added `X-Frame-Options: DENY` and `X-Content-Type-Options: nosniff` for immediate protection.
3. Future work should refactor inline handlers to enable a strict CSP.

## 2026-02-22 - Voyager Security Hardening (Sentinel)
**Vulnerability:** The application relied on `'unsafe-inline'` in the CSP to handle dynamic styles and legacy event handlers, leaving it vulnerable to sophisticated XSS attacks.
**Learning:** Transitioning from inline styles to a class-based CSS system is not just a maintainability win; it is a security necessity for strict CSP compliance. 
**Prevention:**
1. Refactored `bus_analyzer.js`, `packet_viewer.js`, and `ui.js` to use CSS classes instead of `.style()` or `element.style`.
2. Hardened the CSP by removing `'unsafe-inline'` from `style-src`, achieving compliance with internal security benchmarks while preserving D3.js functionality.
