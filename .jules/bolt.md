## 2026-05-23 - [CCSDS Telemetry Performance]
**Learning:** Redundant CRC calculations in API endpoints can severely impact performance. When generating new data packets that include a CRC, validating that CRC immediately afterwards is redundant work.
**Action:** Always serialize the packet once, store the raw bytes, and assume validity for newly generated data. Use `bytes.hex()` for efficient hex dumps.

## 2026-05-24 - [Memory Simulation Optimization]
**Learning:** Simulating hardware memory using Python lists (`[0] * size`) incurs massive overhead (~28 bytes per integer + pointers). For strictly typed data like 12-bit EDAC codes, `array('H')` provides ~18x better memory efficiency and ~40x faster initialization/access.
**Action:** Use `array.array` with appropriate type codes (e.g., 'H' for unsigned short) for large, uniform numeric data structures instead of lists.

## 2026-05-25 - [Startup Time Optimization with Bitwise Logic]
**Learning:** Module-level initialization of large lookup tables (e.g., 4096 entries for Hamming code) using list comprehensions can be surprisingly slow (~28ms) due to list allocation overhead. Replacing list manipulations with explicit bitwise operations using `int.bit_count()` and masks reduced this to ~5.5ms (5x speedup).
**Action:** When initializing large constant tables, prefer direct bitwise calculation over intermediate list/string operations, especially for startup-critical modules.

## 2026-02-22 - [Secure Key Validation]
**Learning:** Naive string comparison for API keys is vulnerable to timing attacks. Even in a serverless environment, use `secrets.compare_digest` for all authentication checks.
**Action:** Implemented constant-time key validation in `verify_api_key`.

## 2026-02-22 - [D3.js Scale Correction]
**Learning:** Incorrect D3 scale functions (e.g., `scaleStep` for continuous data) cause silent rendering failures. `scaleLinear` ensures valid SVG path coordinates for time-series data.
**Action:** Corrected `bus_analyzer.js` scaling to fix the Logic Analyzer graph.

## 2026-02-23 - [CAN Bus Arbitration Optimization]
**Learning:** Bitwise simulation of hardware protocols (like CAN arbitration) in Python loops is extremely slow compared to mathematical equivalents (e.g., `min()`). When the intermediate simulation steps are not observable, replace with the high-level equivalent.
**Action:** Identify loops that simulate physical processes bit-by-bit and replace them with algorithmic equivalents if possible.

## 2026-02-23 - [Avoid String Creation in High-Frequency Loops]
**Learning:** `MemoryBank.read` was creating a new status string via dict lookup for every read, even when the status was ignored. This added ~0.08µs overhead per call (18% slowdown).
**Action:** When a method returns multiple values (e.g., value + status), provide a "fast" variant returning primitive types (integers) to avoid object creation overhead in critical loops.

## 2026-06-01 - [Optimized Unprotected Memory Storage]
**Learning:** `array('H')` (unsigned short) was used for all memory storage, but unprotected memory only stores 8-bit data. Switching to `array('B')` (unsigned char) for unprotected memory reduces memory usage by 50% for large simulated components like Mass Memory.
**Action:** Always check if the data structure fits the actual data width. Use `array` typecodes appropriately to save memory.

## 2026-06-15 - [Loop Fusion in Table Initialization]
**Learning:** Initializing multiple parallel lookup tables using separate list comprehensions iterates over the same range multiple times and incurs list resizing overhead. Pre-allocating the target structures and populating them in a single loop reduced initialization time by ~50% (from ~22ms to ~10ms).
**Action:** When initializing related lookup tables, fuse the loops and pre-allocate memory to improve startup performance.
