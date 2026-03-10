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

## 2026-06-16 - [Pre-compiling Structs and Inlining for Binary Serialization]
**Learning:** High-frequency binary serialization (like generating simulated CCSDS packets) using `struct.pack()` with an inline format string recompiles the format on every call. Pre-compiling to a module-level `struct.Struct()` and inlining the argument preparation to avoid helper function calls yielded a ~16% speedup for packet generation.
**Action:** Always pre-compile `struct` format strings if they are used in high-throughput hot paths. Consider inlining very small helper methods in these loops to avoid Python function call overhead.

## 2026-06-16 - [Fast CRC Validation]
**Learning:** Validating a CRC by recalculating it and comparing requires slicing the packet and unpacking the appended CRC. The CRC-16-CCITT algorithm guarantees that running the calculation over the entire packet (including the appended CRC) results in 0 if no errors occurred.
**Action:** Use `cls.calculate_crc(raw_bytes) == 0` instead of byte slicing and comparing to validate the packet for a ~3.5x speedup.

## 2025-02-28 - [RateLimiter deque sliding window]
**Learning:** The rate limiter implementation initially filtered out old requests using list comprehensions (`[t for t in history if now - t < period]`). Since this is called on every request, it requires an O(N) allocation and full copy where N is the number of recent requests. Using a `collections.deque` and popping from the left (`popleft()`) changes this to an O(1) operation per old request.
**Action:** When implementing rolling/sliding windows of time-series events where items are always appended chronologically, always use `collections.deque` instead of `list` to allow efficient removal of outdated elements from the head.

## 2026-06-25 - [O(N²) I2C Data Buffer Allocation]
**Learning:** In streaming protocols like I2C, buffering bytes in a Python list `[]` and consuming chunks via list slicing `buffer = buffer[length:]` causes a complete reallocation and O(N) copy of all remaining elements for every read operation. This results in O(N²) behavior for continuous streams. Using `bytearray` and `del buffer[:length]` utilizes Python's underlying C `memmove` which avoids deep object copies.
**Action:** When implementing FIFO byte buffers that are frequently appended to and sliced from the front, use `bytearray` instead of lists, and use `del` or `popleft` to consume data without reallocating the remainder of the buffer.

## 2026-06-25 - [Batching API Calls]
**Learning:** Making separate parallel HTTP requests for telemetry and status incurs significant network latency overhead, especially in high-latency environments.
**Action:** Batch related data into a single API endpoint to reduce round-trips from the frontend.

## 2026-06-25 - [Fast List Sorting / Min / Max]
**Learning:** Using `lambda n: n.id` inside `min()`, `max()`, or `sort()` results in significant overhead from repeatedly calling Python functions inside an inner loop. Using `operator.attrgetter('id')` is implemented in C and runs roughly ~30% faster for O(N) operations.
**Action:** When finding extremes or sorting lists of objects by an attribute, use `operator.attrgetter` (or `operator.itemgetter` for dicts) instead of lambdas for improved performance.

## 2026-03-10 - [EDAC Table Memory Optimization]
**Learning:** Python lists of integers have significant overhead (pointer array + individual `int` objects). Converting a dense lookup table of 8-bit integers to a `bytes` object (and other tables to `tuple`s) significantly reduces memory footprint and improves read access times by ~40% for high-frequency operations.
**Action:** When initializing large global lookup tables for 8-bit values, cast them to `bytes` or `tuple` to save memory and slightly improve read performance.
