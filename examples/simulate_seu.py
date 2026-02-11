import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from voyager.memory import MemoryBank

# Write critical data to memory
ram = MemoryBank(size=1024, protected=True)
addr = 0x50
data = 0xFF
ram.write(addr=addr, data=data)
print(f"Written {hex(data)} to addr {hex(addr)}.")

# Simulate Radiation Hit (Bit flip)
bit_to_flip = 3
ram.inject_seu(addr=addr, bit=bit_to_flip)
print(f"Injected SEU at bit {bit_to_flip} (of 12-bit encoded word).")

# Read back with scrubbing
data_read, status = ram.read_with_scrub(addr=addr)
print(f"Read back data: {hex(data_read)}")
print(f"Status: {status}")

if data_read == data and status == "CORRECTED_SINGLE_BIT_ERROR":
    print("SUCCESS: Error was detected and corrected.")
else:
    print("FAILURE: Error correction failed.")
