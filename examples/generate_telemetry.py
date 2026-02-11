import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from voyager.ccsds import TelemetryPacket

# Create a packet from a Magnetometer reading
packet = TelemetryPacket(
    apid=0x10,             # Application Process ID
    sequence_count=42,
    data=bytes([0x01, 0xFF, 0xA2]) # Raw payload
)

print("Generated CCSDS Packet:")
print(packet.hex_dump())
