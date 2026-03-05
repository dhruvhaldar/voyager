class I2CBus:
    def __init__(self, frequency=100000):
        self.frequency = frequency
        self.slaves = {}

    def attach_slave(self, address, slave):
        self.slaves[address] = slave

    def write(self, address, data):
        """Simulate Master writing to Slave."""
        if address not in self.slaves:
            # NACK
            return False, "NACK"

        slave = self.slaves[address]
        # Simulate ACK
        # Write data to slave
        slave.receive(data)

        return True, "ACK"

    def read(self, address, length):
        """Simulate Master reading from Slave."""
        if address not in self.slaves:
            # NACK
            return None, "NACK"

        slave = self.slaves[address]
        data = slave.transmit(length)

        return data, "ACK"

class Slave:
    def __init__(self, address):
        self.address = address
        # Optimization: Use bytearray instead of a list for the data buffer.
        # This avoids O(N) list reallocations and deep copies during transmission.
        self.data_buffer = bytearray()

    def receive(self, data):
        self.data_buffer.extend(data)

    def transmit(self, length):
        # Optimization: Delete the sliced prefix from the bytearray.
        # In CPython, deleting from the front of a bytearray uses memmove,
        # which is significantly faster than slicing and reassigning a list
        # (which requires allocating a new list and copying pointers).
        res = self.data_buffer[:length]
        del self.data_buffer[:length]
        # Return as list to maintain backward compatibility with callers expecting an iterable of integers
        return list(res)
