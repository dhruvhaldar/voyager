## 2026-05-23 - [CCSDS Telemetry Performance]
**Learning:** Redundant CRC calculations in API endpoints can severely impact performance. When generating new data packets that include a CRC, validating that CRC immediately afterwards is redundant work.
**Action:** Always serialize the packet once, store the raw bytes, and assume validity for newly generated data. Use `bytes.hex()` for efficient hex dumps.
