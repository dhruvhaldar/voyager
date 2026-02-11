from .fdir import EDAC

class MemoryBank:
    def __init__(self, size=1024, protected=False):
        self.size = size
        self.protected = protected
        self.memory = [0] * size

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
            decoded, status = EDAC.decode(val)
            return decoded
        else:
            return val

    def read_with_scrub(self, addr):
        if not self.protected:
            return self.read(addr), "OK"

        if addr < 0 or addr >= self.size:
            raise IndexError("Memory access out of bounds")

        val = self.memory[addr]
        decoded, status = EDAC.decode(val)

        if status == "CORRECTED_SINGLE_BIT_ERROR":
            # Scrub: write back corrected value
            # We re-encode the corrected data to ensure parity bits are also correct
            self.memory[addr] = EDAC.encode(decoded)

        return decoded, status

    def inject_seu(self, addr, bit):
        if addr < 0 or addr >= self.size:
            raise IndexError("Memory access out of bounds")

        # Flips the bit at 'bit' index of the stored word.
        self.memory[addr] ^= (1 << bit)
