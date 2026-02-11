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
        self.data_buffer = []

    def receive(self, data):
        self.data_buffer.extend(data)

    def transmit(self, length):
        # Simplistic: return stored buffer or zeros
        res = self.data_buffer[:length]
        self.data_buffer = self.data_buffer[length:]
        return res
