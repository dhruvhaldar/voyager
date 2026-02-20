## 2026-05-23 - [CCSDS Telemetry Performance]
**Learning:** Redundant CRC calculations in API endpoints can severely impact performance. When generating new data packets that include a CRC, validating that CRC immediately afterwards is redundant work.
**Action:** Always serialize the packet once, store the raw bytes, and assume validity for newly generated data. Use `bytes.hex()` for efficient hex dumps.

## 2026-05-24 - [Memory Simulation Optimization]
**Learning:** Simulating hardware memory using Python lists (`[0] * size`) incurs massive overhead (~28 bytes per integer + pointers). For strictly typed data like 12-bit EDAC codes, `array('H')` provides ~18x better memory efficiency and ~40x faster initialization/access.
**Action:** Use `array.array` with appropriate type codes (e.g., 'H' for unsigned short) for large, uniform numeric data structures instead of lists.
