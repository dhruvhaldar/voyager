## 2026-07-04 - [RateLimiter Attribute Access Optimization]
**Learning:** In highly frequent middleware like `RateLimiter`, looking up instance attributes (`self.period`, `self.max_entries`) repeatedly inside methods adds `LOAD_ATTR` bytecode overhead. Looking up local variables (`LOAD_FAST`) is marginally faster.
**Action:** Always assign frequently accessed instance attributes (like `self.period`) to local variables at the beginning of the hot path to avoid redundant object attribute lookups.

## 2026-07-05 - [Loop-Invariant Arithmetic Hoisting]
**Learning:** Calculating mathematical expressions (e.g. `now - period`) inside loop conditions (especially list comprehensions executed during memory cleanup on thousands of entries) results in repeated, redundant float arithmetic, wasting CPU cycles.
**Action:** Hoist loop-invariant calculations by calculating the value once into a local variable (`cutoff = now - period`) before entering loops.
## 2026-07-06 - [FastAPI Threadpool Overhead for Sync Endpoints]
**Learning:** Defining FastAPI endpoints with standard synchronous `def` causes the framework to execute them in an external threadpool (via `anyio.to_thread.run_sync`) to prevent blocking the main event loop. For fast, purely in-memory operations with no blocking I/O (like reading local dictionaries or modifying small objects), this thread dispatch overhead is significantly slower than running them directly on the event loop.
**Action:** Always define fast, non-blocking FastAPI endpoints (those without synchronous file I/O, database calls, or network requests) using `async def` instead of `def` to avoid threadpool overhead.

## 2026-07-08 - [Caching Derived Data on FastAPI Request State]
**Learning:** In FastAPI, identical dependencies or utility functions (like `get_client_ip()`) are often called multiple times per request lifecycle (e.g., first by a RateLimiter middleware/dependency, then by Authentication, then by route-level logging). Re-extracting, decoding, and sanitizing the same header data repeatedly wastes CPU.
**Action:** When deriving data from a request that will likely be needed again, check if `request.state` exists, and cache the computed value there (e.g., `request.state.client_ip = ip`). Return the cached value on subsequent calls to bypass redundant string manipulation and regex execution.

## 2026-07-09 - [Pre-compiling Regex in Hot Paths]
**Learning:** Calling `re.sub(pattern, ...)` inside a high-frequency function (like IP extraction in a middleware) forces the regex engine to parse and lookup the pattern in its internal cache on every request.
**Action:** Always pre-compile regular expressions (`re.compile(...)`) at the module level when they are used in hot paths. This avoids the cache lookup and execution overhead, resulting in ~2x faster string matching/substitution operations.

## 2026-07-10 - [Avoid Unnecessary List Comprehensions in Middleware]
**Learning:** Re-allocating lists using comprehension `[(k, v) for k, v in headers if k != b"server"]` unconditionally in high-frequency middleware is wasteful when the condition (e.g. presence of `Server` header) is rarely met. A simple pre-check loop `for k, _ in headers: if k == b"server"` avoids allocating a new list entirely in the common case.
**Action:** When filtering collections in a hot path where modifications are rare, check for the presence of the condition first before applying the filter to avoid unnecessary memory allocation and overhead.

## 2026-07-12 - [Replace BaseHTTPMiddleware with Pure ASGI Middleware]
**Learning:** `BaseHTTPMiddleware` in FastAPI (inherited from Starlette) introduces significant performance overhead because it creates a new task and uses an asynchronous queue to stream the response for every request.
**Action:** When creating middleware that simply intercepts or modifies request/response headers, use a pure ASGI middleware class that wraps the `send` callable. This avoids the task/queue overhead and is roughly 3-4x faster for high-throughput endpoints.

## 2026-07-13 - [DOM Manipulation Optimization: textContent vs innerText/innerHTML]
**Learning:** Using `innerText` triggers synchronous layout calculations (reflows) because it accounts for CSS styling (like `display: none`), causing significant layout thrashing in high-frequency polling dashboards. Similarly, assigning to `innerHTML` forces the browser to invoke the HTML parser, adding unnecessary overhead when only updating text or clearing a node.
**Action:** Always prefer `textContent` over `innerText` for getting or setting text in DOM nodes. When clearing elements, use `.textContent = ''` instead of `.innerHTML = ''` to bypass parsing overhead completely.

## 2026-07-15 - [Pause Polling on Inactive Tabs]
**Learning:** `setInterval` for polling API endpoints continues firing even when the user's tab is hidden/inactive, which unnecessarily consumes client CPU, network bandwidth, and server resources.
**Action:** Always check `document.hidden` at the start of recurring polling functions and return early if true to pause execution when the tab is inactive.

## 2026-07-20 - [In-Place List Mutation via Backward Iteration in Middleware]
**Learning:** In high-frequency ASGI middleware, filtering a list of tuples (like HTTP headers) using a list comprehension (e.g. `[h for h in headers if h[0] != b"server"]`) needlessly allocates a new list object on every request.
**Action:** When filtering or modifying a list in a hot path, iterate backwards over the list (`for i in range(len(headers) - 1, -1, -1):`) and use `del headers[i]` to remove elements in-place. This preserves index validity during iteration, avoids list allocations entirely, and is significantly faster.
