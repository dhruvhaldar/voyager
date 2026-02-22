# Voyager

Voyager is a web-based emulator for EF2262 Data Handling Systems for Satellites. It allows engineers to architect virtual satellite buses, generate standard-compliant telemetry, and test Fault Detection, Isolation, and Recovery (FDIR) algorithms against simulated hardware failures.

The tool focuses on the "Software-in-the-Loop" aspect of OBDH (On-Board Data Handling), bridging the gap between abstract protocols and physical data movement.

## 📚 Syllabus Mapping (EF2262)

This project strictly adheres to the course learning outcomes:

| Module           | Syllabus Topic                 | Implemented Features                                                                                    |
| :--------------- | :----------------------------- | :------------------------------------------------------------------------------------------------------ |
| **Architecture** | Functions and components       | Simulation of OBC, Mass Memory (SSR), and Payload interactions.                                         |
| **Interfaces**   | UART, I2C, SPI, CAN, Spacewire | Protocol-level simulation of bus arbitration, addressing, and throughput limits.                        |
| **Standards**    | CCSDS                          | Full implementation of CCSDS Space Packet Protocol (headers, secondary headers, CRC).                   |
| **Reliability**  | Error detection (FDIR)         | EDAC (Error Detection and Correction) simulation for memory, Watchdog timers, and Redundancy switching. |
| **Physics**      | Electrophysical aspects        | Simulation of EMI-induced bit flips (Single Event Upsets) and transmission line noise.                  |

## 🚀 Deployment (Vercel)

Voyager runs as a serverless avionics testbed.

1.  **Fork** this repository.
2.  **Deploy** to Vercel (the `api/` folder is detected automatically).
3.  **Configure Environment Variables**:
    - In Vercel Project Settings, add `VOYAGER_API_KEY`.
    - Set it to a secure string (e.g., `my-secure-avionics-key`).
    - *Note: If not set, a random key is generated on every request, which will cause 401 errors.*
4.  **Access** the Avionics Dashboard at `https://your-voyager.vercel.app`.
5.  **Authenticate**: Enter your chosen key when prompted by the dashboard.

## 📊 Artifacts & Avionics Analysis

### 1. The CCSDS Packet Inspector

Visualizes the structure of space packets, breaking down the bit-level headers defined by the Consultative Committee for Space Data Systems.

**Code:**

```python
from voyager.ccsds import TelemetryPacket

# Create a packet from a Magnetometer reading
packet = TelemetryPacket(
    apid=0x10,             # Application Process ID
    sequence_count=42,
    data=bytes([0x01, 0xFF, 0xA2]) # Raw payload
)

print(packet.hex_dump())
# Output: 08 10 C0 2A 00 03 01 FF A2 [CRC]
```

**Artifact Output:**

*Figure 1: Packet Decomposition. The visualizer highlights the Primary Header (identifying the source APID), the Sequence Control (detecting lost packets), and the Packet Error Control (CRC checksum).*

### 2. Bus Traffic Analyzer (Logic Analyzer)

Simulates the timing and arbitration on shared data buses like CAN or I2C.

**Code:**

```python
from voyager.buses import CANBus, Node

# Simulation: Sun Sensor (High Priority) vs Camera (Low Priority)
bus = CANBus(bit_rate=500000)
sun_sensor = Node(id=0x001, bus=bus) # Lower ID = Higher Priority
camera     = Node(id=0x100, bus=bus)

# Both attempt to transmit simultaneously
bus.arbitrate(nodes=[sun_sensor, camera])
```

**Artifact Output:**

*Figure 2: Bus Arbitration. The timeline shows the dominant (0) and recessive (1) bits on the CAN line. The Sun Sensor wins arbitration because its ID (0x001) has more leading zeros, forcing the Camera to back off and retry—a critical concept for deterministic control.*

### 3. FDIR: Single Event Upset (SEU) Recovery

Simulates a radiation-induced bit flip in memory and the OBC's recovery response.

**Code:**

```python
from voyager.memory import MemoryBank
from voyager.fdir import EDAC

# Write critical data to memory
ram = MemoryBank(size=1024, protected=True)
ram.write(addr=0x50, data=0xFF)

# Simulate Radiation Hit (Bit flip)
ram.inject_seu(addr=0x50, bit=3) # 0xFF (11111111) -> 0xF7 (11110111)

# Read back with scrubbing
data, status = ram.read_with_scrub(addr=0x50)
print(f"Data: {hex(data)}, Status: {status}")
# Output: Data: 0xFF, Status: CORRECTED_SINGLE_BIT_ERROR
```

**Artifact Output:**

*Figure 3: EDAC Cycle. The diagram shows the Hamming Code check bits detecting the anomaly. The system transparently corrects the single-bit error (scrubbing) and logs the event to the health status register.*

## 🧪 Testing Strategy

### Unit Tests (Protocol Compliance)

Located in `tests/unit/`.

Example: `tests/unit/test_ccsds.py`

```python
def test_crc_validation():
    """Verifies that the Packet Error Control field correctly detects corruption."""
    pkt = TelemetryPacket(apid=10, data=b'Hello')
    raw_bytes = bytearray(pkt.to_bytes())

    # Corrupt one bit
    raw_bytes[4] ^= 0x01

    assert TelemetryPacket.validate_crc(raw_bytes) == False
```

### E2E Tests (System Redundancy)

Located in `tests/e2e/`.

Example: `tests/e2e/test_watchdog.py`

```python
def test_watchdog_reboot():
    """
    E2E Test: Does the Watchdog Timer (WDT) reset the OBC if software hangs?
    """
    obc = OnBoardComputer()
    obc.boot()

    # Simulate software hang (infinite loop, no WDT kick)
    obc.freeze()

    # Advance time past WDT timeout
    simulation.step(seconds=5.0)

    assert obc.reboot_count == 1
    assert obc.mode == "SAFE_MODE"
```

## ⚖️ License

MIT License

Copyright (c) 2026 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files... [Standard MIT Text]
