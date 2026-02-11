import pytest
import struct
from voyager.ccsds import TelemetryPacket

def test_packet_creation():
    # Create a packet from a Magnetometer reading
    packet = TelemetryPacket(
        apid=0x10,             # Application Process ID
        sequence_count=42,
        data=bytes([0x01, 0xFF, 0xA2]) # Raw payload
    )

    # Check headers
    # We expect valid CCSDS headers.
    # The length field depends on CRC size.
    # With CRC-16 (2 bytes), length = 3 + 2 - 1 = 4.

    raw_bytes = packet.to_bytes()
    assert len(raw_bytes) == 6 + 3 + 2 # Header(6) + Data(3) + CRC(2)

    # Check primary header
    # 08 10 C0 2A 00 04
    assert raw_bytes[0] == 0x08
    assert raw_bytes[1] == 0x10
    assert raw_bytes[2] == 0xC0
    assert raw_bytes[3] == 0x2A
    assert raw_bytes[4] == 0x00
    # assert raw_bytes[5] == 0x03 # If we strictly followed the example
    assert raw_bytes[5] == 0x04 # Since we use CRC-16

    # Check payload
    assert raw_bytes[6] == 0x01
    assert raw_bytes[7] == 0xFF
    assert raw_bytes[8] == 0xA2

def test_crc_validation():
    """Verifies that the Packet Error Control field correctly detects corruption."""
    pkt = TelemetryPacket(apid=10, sequence_count=1, data=b'Hello')
    raw_bytes = bytearray(pkt.to_bytes())

    # Verify valid CRC first
    assert TelemetryPacket.validate_crc(raw_bytes) == True

    # Corrupt one bit in data
    raw_bytes[6] ^= 0x01

    assert TelemetryPacket.validate_crc(raw_bytes) == False

def test_crc_validation_header_corruption():
    """Verifies that CRC detects header corruption."""
    pkt = TelemetryPacket(apid=10, sequence_count=1, data=b'Hello')
    raw_bytes = bytearray(pkt.to_bytes())

    # Corrupt one bit in header
    raw_bytes[0] ^= 0x01

    assert TelemetryPacket.validate_crc(raw_bytes) == False
