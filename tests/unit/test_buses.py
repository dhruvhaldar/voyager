import pytest
from voyager.buses import CANBus, Node, I2CBus, Spacewire

def test_can_arbitration():
    bus = CANBus(bit_rate=500000)
    sun_sensor = Node(id=0x001, bus=bus) # High Priority
    camera     = Node(id=0x100, bus=bus) # Low Priority

    # Both attempt to transmit simultaneously
    winner = bus.arbitrate(nodes=[sun_sensor, camera])

    assert winner.id == sun_sensor.id

    # Check if only one node, it wins
    winner = bus.arbitrate(nodes=[camera])
    assert winner.id == camera.id

    # Check with same ID (should win but ideally shouldn't happen on bus)
    winner = bus.arbitrate(nodes=[sun_sensor, sun_sensor])
    assert winner.id == sun_sensor.id

def test_i2c_transfer():
    bus = I2CBus(frequency=100000)

    # Mock slave
    class MockSlave:
        def __init__(self, addr):
            self.addr = addr
            self.buffer = []
        def receive(self, data):
            self.buffer.extend(data)
        def transmit(self, length):
            ret = self.buffer[:length]
            self.buffer = self.buffer[length:]
            return ret

    slave = MockSlave(0x50)
    bus.attach_slave(0x50, slave)

    # Write
    success, status = bus.write(0x50, [0x01, 0x02])
    assert success
    assert status == "ACK"
    assert slave.buffer == [0x01, 0x02]

    # Read
    data, status = bus.read(0x50, 2)
    assert data == [0x01, 0x02]
    assert status == "ACK"
    assert slave.buffer == []

    # Invalid address
    success, status = bus.write(0x60, [0xFF])
    assert not success
    assert status == "NACK"

def test_spacewire_routing():
    sw = Spacewire(bit_rate=100000000)

    # Add routers
    sw.add_router(0x10, "Router A")
    sw.add_router(0x20, "Router B")

    success, msg = sw.route(0x10, 0x20, b"Packet")
    assert success
    assert "delivered" in msg

    success, msg = sw.route(0x10, 0x30, b"Packet")
    assert not success
    assert "unreachable" in msg
