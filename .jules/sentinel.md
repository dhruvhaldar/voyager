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

## 2026-02-22 - Unauthenticated Command Injection
**Vulnerability:** Critical simulation control endpoints (`/api/command/reboot`, `/api/command/freeze`) were exposed without authentication, allowing unprivileged users to disrupt the avionics testbed.
**Learning:** In "serverless" or micro-frontend architectures, developers may overlook securing API routes that are intended for internal use but are actually public.
**Prevention:**
1. Enforced API Key authentication using FastAPI's `Security` dependency on all state-changing endpoints.
2. Implemented a secure-by-default generated key mechanism for local development.

## 2026-03-01 - Watchdog Bypass via Infinite Simulation Timestep
**Vulnerability:** The `OnBoardComputer.tick(dt)` method validated that `dt` was non-negative to prevent reversing time, but failed to check if `dt` was finite. An attacker could pass `Infinity` via the `/api/tick?dt=inf` endpoint. This caused the watchdog timer to immediately reach `inf`, forcing a reboot into `SAFE_MODE` and disrupting the simulation, effectively acting as a Denial of Service.
**Learning:** While framework-level validation (like FastAPI's `Query(ge=0)`) ensures numbers meet boundary conditions, standard float types still accept `inf` and `nan`. These special values can break business logic or cause JSON serialization errors further down the stack.
**Prevention:**
1. Added an explicit `math.isfinite(dt)` check in the domain model (`voyager/obc.py`) to raise a `ValueError` for infinite or NaN inputs.
2. Remember that float inputs from external sources must always be validated for finiteness unless specifically designed to handle `inf`/`nan`.

## 2026-03-01 - Proxy Rate Limiting DoS & Memory Exhaustion
**Vulnerability:** The `RateLimiter` relied on `request.client.host` to identify clients, which resolves to the reverse proxy's IP in serverless environments like Vercel. This allowed a single client to exhaust the rate limit and trigger a Denial of Service (DoS) for all legitimate users. Furthermore, `self.history` tracked IPs without a size cap, exposing an Out-Of-Memory (OOM) vector if an attacker rotated spoofed IPs or a botnet flooded the endpoint.
**Learning:** Rate limiting logic must be proxy-aware (`X-Forwarded-For` or `X-Real-IP`) when deployed behind load balancers or edge networks. Additionally, in-memory data structures used for security controls must have strict upper bounds to prevent memory exhaustion DoS.
**Prevention:**
1. Updated `RateLimiter` to check `X-Forwarded-For` and `X-Real-IP` headers before falling back to `request.client.host`.
2. Implemented an OOM protection cap (`max_entries=10000`) on `self.history`, clearing expired IPs or flushing the dictionary entirely to ensure the service remains available during high-volume attacks.

## 2026-03-01 - 500 Internal Server Error Traceback Leak
**Vulnerability:** When a `ValueError` was thrown in the domain model (e.g., passing `dt=inf` or `dt=nan` to `/api/tick`), FastAPI allowed the exception to bubble up unhandled. This caused a `500 Internal Server Error`, which in some deployment configurations could leak a stack trace to the client, exposing internal implementation details.
**Learning:** Framework-level type validations (like `float`) often accept edge cases (like `inf` or `nan`). While the domain model correctly rejected these via a `ValueError`, failing to handle that specific error type gracefully at the API boundary left the application susceptible to returning verbose 500 errors during a DoS attempt. In addition, globally masking `ValueError`s can hide legitimate internal server bugs.
**Prevention:**
1. Created a specialized domain exception `SimulationError` (inheriting from `ValueError`) to distinguish intentional domain validation failures from generic `ValueError`s.
2. Updated the domain logic (`voyager/obc.py`) to raise `SimulationError`.
3. Added an exception handler for `SimulationError` in `api/index.py` using `@app.exception_handler(SimulationError)` that returns a sanitized `400 Bad Request`.

## 2026-03-02 - Missing Strict-Transport-Security Header
**Vulnerability:** The application was missing the `Strict-Transport-Security` (HSTS) header in API responses, which left it vulnerable to downgrade attacks (e.g., SSL stripping) if deployed over HTTPS.
**Learning:** While other security headers (like CSP, X-Frame-Options) were present, HSTS is a critical component for enforcing secure connections at the browser level and should always be included in web applications.
**Prevention:**
1. Added the `Strict-Transport-Security: max-age=31536000; includeSubDomains` header to the global HTTP middleware in `api/index.py`.
2. Added an assertion to `tests/test_security_headers.py` to ensure the header remains present in future changes.

## 2026-03-03 - Insufficient Content-Security-Policy Directives
**Vulnerability:** The Content-Security-Policy header lacked directives like `frame-ancestors`, `base-uri`, and `upgrade-insecure-requests`, leaving the application potentially exposed to UI redressing (clickjacking) in modern browsers, base tag injection, and insecure network transitions.
**Learning:** Setting basic CSP `*-src` directives isn't always enough to secure a web app. `X-Frame-Options` is deprecated in modern browsers in favor of `frame-ancestors`. Using `upgrade-insecure-requests` prevents mixed content issues when assets are loaded without HTTPS, and `base-uri 'none'` restricts a common attack vector where the base tag is injected to redirect relative URLs.
**Prevention:**
1. Appended `frame-ancestors 'none'; base-uri 'none'; upgrade-insecure-requests;` to the existing `Content-Security-Policy` header in the FastAPI middleware (`api/index.py`).
2. Augmented `tests/test_security_headers.py` to verify the presence of these crucial CSP directives.

## 2026-03-05 - Complete Eradication of innerHTML in Frontend
**Vulnerability:** Several instances of `innerHTML` assignment remained in `public/packet_viewer.js` and `public/ui.js` for handling dynamic UI updates (e.g., button state changes, confirmation prompts). While some data sources were static strings or trusted backend variables, using `innerHTML` to update DOM state intrinsically exposes the application to Cross-Site Scripting (XSS) risks if assumptions about data provenance fail.
**Learning:** Any use of `innerHTML` is an anti-pattern when security is a priority. "Safe" static string assignments (`element.innerHTML = '<span>Safe</span>'`) can easily be refactored by future developers into unsafe ones (`element.innerHTML = '<span>' + userInput + '</span>'`). Defense-in-depth dictates enforcing strict pure DOM manipulation (`textContent` and `createElement`) application-wide.
**Prevention:**
1. Replaced all occurrences of `innerHTML` in `packet_viewer.js` and `ui.js` with pure DOM node creation, traversal, and text content assignment (e.g., using `document.createElement`, `textContent`, and `appendChild`).
2. Implemented node cloning (`cloneNode(true)`) and arrays to persist button states instead of serializing their contents into HTML strings.

## 2026-03-07 - Rate Limiter Bypass via Authentication Short-Circuit
**Vulnerability:** The rate limiter on sensitive endpoints (`/api/command/reboot`, `/api/command/freeze`) was defined after the authentication check (`dependencies=[Depends(verify_api_key), Depends(limit_sensitive)]`). This allowed an unauthenticated attacker to bypass the rate limiter entirely, as the `verify_api_key` dependency would raise a `401 Unauthorized` before `limit_sensitive` could evaluate the request and increment the limit counter. This could enable a denial-of-service attack against the authentication mechanism or underlying systems.
**Learning:** When combining multiple security dependencies in FastAPI, the order of evaluation matters. Rate limiting should always precede authentication so that both authenticated and unauthenticated malicious traffic can be effectively throttled.
**Prevention:**
1. Swapped the order of dependencies in FastAPI route definitions to `dependencies=[Depends(limit_sensitive), Depends(verify_api_key)]`.
2. Added a test in `tests/test_rate_limit_auth_bypass.py` to assert that rate limiting is enforced even for unauthenticated requests.

## 2026-03-08 - Missing Subresource Integrity (SRI) on External Scripts
**Vulnerability:** The `d3.v7.min.js` script was loaded from a third-party Content Delivery Network (CDN) without a Subresource Integrity (SRI) attribute. If the CDN were compromised, an attacker could replace the script with malicious code, leading to an XSS attack on all clients.
**Learning:** Loading resources from CDNs is common for performance and caching, but introduces a supply chain vulnerability. Trusting third-party infrastructure blindly is an anti-pattern; defense-in-depth requires validating the integrity of fetched assets.
**Prevention:**
1. Calculated the SHA-384 hash of the intended `d3.v7.min.js` file.
2. Added the `integrity` attribute (with the calculated hash) and `crossorigin="anonymous"` to the `<script>` tag in `public/index.html`. This ensures the browser will refuse to execute the script if its contents change unexpectedly.

## 2026-03-11 - Exposed FastAPI Documentation (Sentinel)
**Vulnerability:** FastAPI automatically generates interactive API documentation at `/docs` and `/redoc`, exposing the API structure, parameters, and endpoints. In a production environment, this leaks the attack surface to potential attackers.
**Learning:** Framework defaults are often optimized for developer experience rather than production security. Always explicitly disable automatic documentation generation in production or secure it behind authentication.
**Prevention:** Set `docs_url=None`, `redoc_url=None`, and `openapi_url=None` when instantiating the `FastAPI` app.

## 2026-06-25 - Authentication Bypass via Simulated Key
**Vulnerability:** The `verify_api_key` dependency allowed unauthenticated access to all endpoints because it returned a "SIMULATED_KEY" string when the key was missing or incorrect instead of raising an HTTP 401 Unauthorized exception. This essentially bypassed the API key enforcement, leaving sensitive simulation commands exposed.
**Learning:** Returning dummy or simulated values during authentication checks is a critical security vulnerability. An authentication dependency must strictly reject unauthorized requests using appropriate HTTP status codes (e.g., 401, 403) rather than passing simulated context to the downstream route handlers.
**Prevention:**
1. Modified `verify_api_key` to explicitly raise `HTTPException(status_code=401)` when the API key is missing or invalid.
2. Updated tests to assert that unauthenticated requests to protected endpoints receive a `401 Unauthorized` response.

## 2026-03-13 - Rate Limiter Bypass via History Wiping
**Vulnerability:** The `RateLimiter` relied on an in-memory dictionary `self.history` to track request counts. To prevent memory exhaustion (OOM), it had a mechanism to clear the entire dictionary (`self.history.clear()`) if it reached `max_entries` and no expired entries could be freed. An attacker could exploit this by flooding the server with requests from randomly spoofed `X-Forwarded-For` IPs. Once the dictionary filled up with unexpired spoofed entries, the next request would trigger `clear()`, completely wiping the rate limit history for all legitimate clients and allowing the attacker to bypass the rate limit indefinitely.
**Learning:** Security controls designed to protect availability (like OOM protection) can inadvertently create bypass vulnerabilities if they fail open or reset state. When a security mechanism is at capacity, it must "fail securely" by denying new unverified requests, prioritizing the integrity of existing state and limits over admitting new potentially malicious clients.
**Prevention:**
1. Modified `RateLimiter` to raise an `HTTPException(429, "Server at capacity")` when `self.history` reaches `max_entries` and cannot be pruned, instead of calling `self.history.clear()`.
2. This ensures that an IP spoofing flood only results in new IPs being blocked, while preserving the rate limit tracking for existing IPs.
## 2024-05-24 - Centralized IP Extraction & Audit Logging
**Vulnerability:** Inconsistent extraction of client IP across endpoints could lead to spoofing (trusting false `X-Forwarded-For` headers) and missed audit trails for sensitive API operations (like missing authentication or executing system-level commands).
**Learning:** Extracting client IP behind a reverse proxy must be standardized. `request.scope.get('client')[0]` handles direct connections, but `X-Forwarded-For` chains need to be iterated backwards to find the trusted edge proxy IP, preventing injection by attackers. Applying this centralized extraction consistently is critical for building accurate audit trails.
**Prevention:** Always use the centralized `get_client_ip(request)` function for rate limiters, auth checks, and sensitive command handlers, logging the IP explicitly to track potential abuse and debugging issues.

## 2023-10-25 - Log Injection (CRLF) via X-Forwarded-For
**Vulnerability:** The application extracted the client IP from the `X-Forwarded-For` header and logged it directly during authorization failures and command executions. An attacker could inject CRLF (`\n`, `\r`) characters into the `X-Forwarded-For` header, leading to Log Injection where they could spoof arbitrary log entries (e.g. `[CRITICAL] HACKED`).
**Learning:** Even though `X-Forwarded-For` is parsed backwards to find the real IP, if the header is completely attacker-controlled (e.g. direct access), it must be sanitized. The `strip()` function only removes leading and trailing whitespace, leaving embedded newlines intact.
**Prevention:** Always sanitize data extracted from HTTP headers before logging. For strings like IPs, stripping newlines (`.replace('\n', '').replace('\r', '')`) prevents log structure manipulation.

## 2026-11-04 - Terminal Log Injection via X-Forwarded-For
**Vulnerability:** The `get_client_ip` function relied on a simple string replacement (`.replace('\n', '').replace('\r', '')`) to sanitize extracted IPs for logging. While this mitigated basic Log Injection (CRLF), it failed to sanitize terminal escape sequences like ANSI color codes (e.g., `\x1b[31m`). An attacker could exploit this by passing a spoofed `X-Forwarded-For` header containing such sequences, resulting in Terminal Log Injection, which can disrupt observability or mask the true nature of the logs.
**Learning:** String stripping for sanitization is generally insufficient for untrusted input. When extracting a predictable format (like an IP address or proxy chain), an explicit allowlist regex is far safer than a blocklist approach, because it prevents unforeseen attack vectors like ANSI injections.
**Prevention:**
1. Updated the `get_client_ip` sanitization in `api/index.py` to use a strict regex allowlist (`re.sub(r'[^a-zA-Z0-9.:\-, ]', '', client_ip)`) that only permits valid IP address characters and common proxy separation syntax.
2. Wrote an automated test `test_terminal_log_injection_prevention` to explicitly verify that terminal escape characters like `\x1b` are stripped prior to logging.

## 2024-05-27 - Unauthenticated DoS via Health Check Flooding
**Vulnerability:** The `/api/health` endpoint, used for server health monitoring, lacked any rate limiting. An attacker could flood this unauthenticated endpoint with high-frequency requests, consuming server resources (CPU, network bandwidth) and potentially causing a Denial of Service (DoS) for legitimate users trying to access the application.
**Learning:** Even benign endpoints like health checks need defense-in-depth protection against abuse. While they must be accessible without authentication to allow load balancers to function, they should be bounded by a generous but strict rate limit that permits normal polling while blocking malicious floods.
**Prevention:**
1. Implemented a dedicated `RateLimiter` for the health check (`limit_health = RateLimiter(calls=1000, period=60.0)`).
2. Added `dependencies=[Depends(limit_health)]` to the `@app.get("/api/health")` route.
3. Wrote `test_rate_limiting_health_endpoint` to enforce this limit in the CI pipeline.

## 2026-11-20 - API Key Persistence via localStorage
**Vulnerability:** The application was storing the sensitive `voyager_api_key` in `localStorage`. This meant the key persisted across browser sessions and tabs, making it vulnerable to extraction if the device was shared, left unattended, or if an XSS vulnerability was exploited later.
**Learning:** For client-side application interactions that don't use secure HttpOnly cookies, storing sensitive credentials (like API keys) in `localStorage` creates an unnecessarily large attack surface.
**Prevention:**
1. Modified `public/packet_viewer.js` and `public/ui.js` to store and retrieve the API key using `sessionStorage` instead of `localStorage`.
2. Updated tests to correctly mock key injection via `sessionStorage`.
