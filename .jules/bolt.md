## 2025-02-12 - CCSDS CRC Optimization
**Learning:** Pure Python implementations of standard algorithms like CRC-16 (0x1021) are drastically slower (~50x) than built-in C extensions. `binascii.crc_hqx(data, 0xFFFF)` is a drop-in replacement for the standard CCSDS CRC algorithm.
**Action:** Always check `binascii` or other standard library C extensions before implementing low-level bit manipulation algorithms in Python.

## 2026-02-17 - Parallel API Requests
**Learning:** The dashboard's update loop (`updateTelemetry`) sequentially fetched independent endpoints (`/telemetry` then `/status`), doubling the latency penalty. Simple `Promise.all` parallelization halves the wait time without architectural changes.
**Action:** Audit all sequential `await fetch()` calls in frontend code to identify independent requests that can be parallelized.

## 2026-02-18 - Batch DOM Updates
**Learning:** Appending elements to the DOM in a loop (`forEach`) causes N reflows, significantly impacting rendering performance for large lists or frequently updated views (like telemetry).
**Action:** Always use `DocumentFragment` to batch DOM insertions into a single reflow.
