## 2025-02-12 - CCSDS CRC Optimization
**Learning:** Pure Python implementations of standard algorithms like CRC-16 (0x1021) are drastically slower (~50x) than built-in C extensions. `binascii.crc_hqx(data, 0xFFFF)` is a drop-in replacement for the standard CCSDS CRC algorithm.
**Action:** Always check `binascii` or other standard library C extensions before implementing low-level bit manipulation algorithms in Python.
