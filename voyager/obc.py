class OnBoardComputer:
    def __init__(self):
        self.mode = "OFF"
        self.reboot_count = 0
        self.watchdog_timer = 0.0
        self.watchdog_timeout = 5.0 # seconds
        self.frozen = False

    def boot(self):
        self.mode = "NORMAL"
        self.frozen = False
        self.watchdog_timer = 0.0
        print("OBC Booted into NORMAL mode.")

    def freeze(self):
        """Simulates software hang."""
        self.frozen = True
        print("OBC Frozen (Software Hang).")

    def kick_watchdog(self):
        """Resets the watchdog timer."""
        self.watchdog_timer = 0.0

    def tick(self, dt):
        """
        Advances the state of the OBC by dt seconds.
        """
        if dt < 0:
            raise ValueError("Time step must be non-negative")

        if self.mode == "OFF":
            return

        if self.frozen:
            # Software is hung, watchdog is not kicked
            self.watchdog_timer += dt
        else:
            # Normal operation: software kicks watchdog periodically
            # We assume normal operation kicks it successfully unless dt is huge
            # But to simulate "freeze", we explicitly use freeze().
            # If not frozen, we assume WDT is kicked.
            self.watchdog_timer = 0.0

        if self.watchdog_timer >= self.watchdog_timeout:
            print(f"Watchdog Timeout ({self.watchdog_timer}s >= {self.watchdog_timeout}s). Rebooting...")
            self.reboot()

    def reboot(self):
        self.reboot_count += 1
        self.mode = "SAFE_MODE"
        self.watchdog_timer = 0.0
        self.frozen = False
        print("OBC Rebooted into SAFE_MODE.")

class Simulation:
    def __init__(self, obc):
        self.obc = obc
        self.time = 0.0

    def step(self, seconds):
        """
        Advances the simulation time.
        """
        # We step in small increments to catch events accurately if needed,
        # or just jump. For WDT, jumping is fine as long as we check logic.
        self.time += seconds
        self.obc.tick(seconds)
