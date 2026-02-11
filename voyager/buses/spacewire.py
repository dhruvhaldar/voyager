class Spacewire:
    def __init__(self, bit_rate=100000000):
        self.bit_rate = bit_rate
        self.routers = {} # Addr -> Router

    def add_router(self, addr, router):
        self.routers[addr] = router

    def route(self, source_addr, dest_addr, packet):
        """
        Simulates Spacewire routing.
        Usually uses path addressing (byte sequence).
        For simplicity, we assume logical addressing or direct routing.
        """
        path = []
        current = source_addr

        # Simple simulation: check if dest is reachable.
        # This function would trace the path.

        if dest_addr in self.routers:
            # Delivered
            return True, f"Packet delivered to {dest_addr} via Wormhole routing."
        else:
            return False, "Destination unreachable."
