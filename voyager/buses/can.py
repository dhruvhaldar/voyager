class Node:
    def __init__(self, id, bus):
        self.id = id
        self.bus = bus

    def __repr__(self):
        return f"Node(id={hex(self.id)})"

class CANBus:
    def __init__(self, bit_rate=500000):
        self.bit_rate = bit_rate

    def arbitrate(self, nodes):
        """
        Simulates CAN bus arbitration among contending nodes.
        The node with the lowest ID (highest priority) wins.
        Returns the winning Node.
        """
        if not nodes:
            return None

        # CAN arbitration logic:
        # Bus is wired-AND (0 is dominant, 1 is recessive).
        # If a node transmits 0 and sees 0, it continues.
        # If a node transmits 1 but sees 0, it lost arbitration and stops.

        # We can simulate this bit by bit for 11-bit standard ID.
        active_nodes = list(nodes)

        for bit_pos in range(10, -1, -1): # 11 bits: 10 down to 0
            if len(active_nodes) <= 1:
                break

            # Check what each node wants to transmit at this bit position
            # If any node transmits 0 (dominant), then the bus state is 0.
            # Nodes transmitting 1 (recessive) lose if bus is 0.

            has_dominant = False
            for node in active_nodes:
                bit = (node.id >> bit_pos) & 1
                if bit == 0:
                    has_dominant = True

            if has_dominant:
                # Filter out nodes transmitting 1
                active_nodes = [n for n in active_nodes if ((n.id >> bit_pos) & 1) == 0]
            else:
                # All transmitted 1, so bus is 1. No one loses yet.
                pass

        return active_nodes[0] if active_nodes else None
