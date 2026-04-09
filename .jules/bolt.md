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
