
import pytest
from array import array
from voyager.memory import MemoryBank

def test_memory_bank_initialization_unprotected():
    """Verify that unprotected memory uses array('B') for efficiency."""
    mem = MemoryBank(size=1024, protected=False)
    assert mem.memory.typecode == 'B'
    assert mem.memory.itemsize == 1
    assert len(mem.memory) == 1024

def test_memory_bank_initialization_protected():
    """Verify that protected memory uses array('H') for EDAC storage."""
    mem = MemoryBank(size=1024, protected=True)
    assert mem.memory.typecode == 'H'
    assert mem.memory.itemsize == 2
    assert len(mem.memory) == 1024

def test_memory_bank_read_write_unprotected():
    """Verify read/write works correctly for unprotected memory."""
    mem = MemoryBank(size=10, protected=False)
    mem.write(0, 0xA5) # 10100101
    assert mem.read(0) == 0xA5

    # Test overflow masking in write
    mem.write(1, 0x1FF) # Should store 0xFF
    assert mem.read(1) == 0xFF

def test_inject_seu_unprotected_valid():
    """Verify SEU injection works for valid bits (0-7) in unprotected memory."""
    mem = MemoryBank(size=10, protected=False)
    mem.write(0, 0x00)

    # Flip bit 0
    mem.inject_seu(0, 0)
    assert mem.read(0) == 0x01

    # Flip bit 7
    mem.inject_seu(0, 7)
    assert mem.read(0) == 0x81 # 10000001

def test_inject_seu_unprotected_invalid():
    """Verify SEU injection raises ValueError for invalid bits (>=8) in unprotected memory."""
    mem = MemoryBank(size=10, protected=False)

    with pytest.raises(ValueError, match="Bit index 8 out of range"):
        mem.inject_seu(0, 8)

    with pytest.raises(ValueError):
        mem.inject_seu(0, 100)

def test_inject_seu_protected_valid():
    """Verify SEU injection works for protected memory."""
    mem = MemoryBank(size=10, protected=True)
    # Write 0 -> encodes to 0 (all 0s, even parity bits usually)
    # EDAC: 0 -> 0x000 (encoded)
    mem.write(0, 0x00)

    # Flip bit 0
    mem.inject_seu(0, 0)
    # Read should correct it transparently
    assert mem.read(0) == 0x00

    # Check raw memory if possible? (No public API, but we can check internal)
    assert mem.memory[0] == 1

def test_inject_seu_protected_high_bits():
    """Verify high bits (12-15) can be flipped in protected memory (16-bit storage) without error."""
    mem = MemoryBank(size=10, protected=True)
    mem.write(0, 0x00)

    # Flip bit 12 (outside EDAC range, but inside storage)
    mem.inject_seu(0, 12)

    # Should not crash.
    # Read should still be 0 (EDAC decoder ignores bits > 11 usually due to mask)
    assert mem.read(0) == 0x00
