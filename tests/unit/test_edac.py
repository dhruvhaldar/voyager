import pytest
from voyager.memory import MemoryBank
from voyager.fdir import EDAC

def test_edac_logic():
    # Test EDAC encoding and decoding logic directly
    data = 0xFF
    encoded = EDAC.encode(data)
    decoded, status = EDAC.decode(encoded)
    assert decoded == data
    assert status == "OK"

    # Test bit flip
    # Flip bit 0 (P1)
    encoded ^= 1
    decoded, status = EDAC.decode(encoded)
    assert decoded == data
    assert status == "CORRECTED_SINGLE_BIT_ERROR"

def test_memory_scrub():
    # Example from README
    ram = MemoryBank(size=1024, protected=True)
    ram.write(addr=0x50, data=0xFF)

    # Simulate Radiation Hit (Bit flip)
    # Flip bit 3 (P4)
    ram.inject_seu(addr=0x50, bit=3)

    # Read back with scrubbing
    data, status = ram.read_with_scrub(addr=0x50)
    assert data == 0xFF
    assert status == "CORRECTED_SINGLE_BIT_ERROR"

    # Check that it was scrubbed (status should be OK next time)
    data, status = ram.read_with_scrub(addr=0x50)
    assert data == 0xFF
    assert status == "OK"

def test_memory_double_flip():
    # With SEC (Single Error Correction), double bit flips might be detected as single or incorrect correction.
    # Our simple Hamming might miscorrect double bit errors if we don't implement SEC-DED.
    # But let's just see behavior.

    ram = MemoryBank(size=1024, protected=True)
    ram.write(addr=0x10, data=0xA5) # 10100101

    # Flip two bits
    ram.inject_seu(addr=0x10, bit=0)
    ram.inject_seu(addr=0x10, bit=1)

    decoded, status = ram.read_with_scrub(addr=0x10)

    # Simple Hamming with 2 errors will report a single error at a wrong location.
    # So status will be "CORRECTED_SINGLE_BIT_ERROR" (incorrectly) or "OK" (if syndrome happens to be 0, unlikely).
    # This is expected behavior for simple Hamming SEC.
    # Just verify it doesn't crash.
    assert status in ["OK", "CORRECTED_SINGLE_BIT_ERROR"]

def test_edac_out_of_bounds():
    # Test out of bounds input handling (should be masked)

    # Encode > 255
    # 0x1FF (511) -> should be treated as 0xFF (255)
    byte_val = 0x1FF
    encoded = EDAC.encode(byte_val)
    # Check that it matches encode(0xFF)
    assert encoded == EDAC.encode(0xFF)

    # Decode > 4095
    # 0x1000 | encoded -> should be treated as encoded
    # Let's take a valid encoded value
    valid_encoded = EDAC.encode(0xAB)
    large_encoded = valid_encoded | 0xF000

    decoded, status = EDAC.decode(large_encoded)
    expected_decoded, expected_status = EDAC.decode(valid_encoded)

    assert decoded == expected_decoded
    assert status == expected_status
