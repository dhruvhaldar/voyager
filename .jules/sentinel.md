## 2025-05-15 - Watchdog Timer Rewind Vulnerability
**Vulnerability:** The simulation's `tick` function accepted negative time deltas (`dt`), allowing an attacker to decrease the watchdog timer and bypass the safe mode reboot mechanism when the system was frozen.
**Learning:** Simulation parameters that affect state accumulation (like timers) must be strictly monotonic. Trusting client-side input for physical properties like "time" can lead to logic bypasses.
**Prevention:**
1. Validated `dt` at the API boundary using Pydantic's `Query(..., ge=0)`.
2. Added a defensive check in the `OnBoardComputer.tick` method to raise `ValueError` for negative inputs.
