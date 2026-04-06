## 2026-07-04 - [RateLimiter Attribute Access Optimization]
**Learning:** In highly frequent middleware like `RateLimiter`, looking up instance attributes (`self.period`, `self.max_entries`) repeatedly inside methods adds `LOAD_ATTR` bytecode overhead. Looking up local variables (`LOAD_FAST`) is marginally faster.
**Action:** Always assign frequently accessed instance attributes (like `self.period`) to local variables at the beginning of the hot path to avoid redundant object attribute lookups.

## 2026-07-05 - [Loop-Invariant Arithmetic Hoisting]
**Learning:** Calculating mathematical expressions (e.g. `now - period`) inside loop conditions (especially list comprehensions executed during memory cleanup on thousands of entries) results in repeated, redundant float arithmetic, wasting CPU cycles.
**Action:** Hoist loop-invariant calculations by calculating the value once into a local variable (`cutoff = now - period`) before entering loops.