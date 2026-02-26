from array import array
from .fdir import EDAC

class MemoryBank:
    def __init__(self, size=1024, protected=False):
        self.size = size
        self.protected = protected
        # Optimization: Use array for memory efficiency and faster access.
        # 'H' is unsigned short (2 bytes), which fits 12-bit EDAC codes perfectly.
        # 'B' is unsigned char (1 byte), which is 2x more efficient for unprotected 8-bit memory.
        if self.protected:
            self.memory = array('H', [0]) * size
        else:
            self.memory = array('B', [0]) * size

    def write(self, addr, data):
        if addr < 0 or addr >= self.size:
            raise IndexError("Memory access out of bounds")

        if self.protected:
            self.memory[addr] = EDAC.encode(data)
        else:
            self.memory[addr] = data & 0xFF

    def read(self, addr):
        if addr < 0 or addr >= self.size:
            raise IndexError("Memory access out of bounds")

        val = self.memory[addr]
        if self.protected:
            # On standard read, EDAC corrects on the fly but doesn't scrub (write back)
            # Optimization: Use decode_data_only to avoid tuple creation and status lookup
            # This is significantly faster for the hot path where status is ignored.
            return EDAC.decode_data_only(val)
        else:
            return val

    def read_with_scrub(self, addr):
        if not self.protected:
            return self.read(addr), "OK"

        if addr < 0 or addr >= self.size:
            raise IndexError("Memory access out of bounds")

        val = self.memory[addr]
        # Optimization: Use decode_fast to avoid intermediate tuple creation and string comparison
        decoded, status_code = EDAC.decode_fast(val)

        if status_code == EDAC.STATUS_CORRECTED:
            # Scrub: write back corrected value
            # We re-encode the corrected data to ensure parity bits are also correct
            self.memory[addr] = EDAC.encode(decoded)

        return decoded, EDAC.STATUS_MAP[status_code]

    def inject_seu(self, addr, bit):
        if addr < 0 or addr >= self.size:
            raise IndexError("Memory access out of bounds")

        # Flips the bit at 'bit' index of the stored word.
        # Check bit index against storage width to prevent OverflowError.

        if self.memory.typecode == 'B': # Unprotected, 8-bit
            if bit >= 8:
                raise ValueError(f"Bit index {bit} out of range for 8-bit memory")
        elif self.memory.typecode == 'H': # Protected, 16-bit
            if bit >= 16:
                raise ValueError(f"Bit index {bit} out of range for 16-bit memory")

        self.memory[addr] ^= (1 << bit)
