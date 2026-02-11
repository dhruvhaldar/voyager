import pytest
from voyager.obc import OnBoardComputer

def test_watchdog_reboot():
    """
    E2E Test: Does the Watchdog Timer (WDT) reset the OBC if software hangs?
    """
    obc = OnBoardComputer()
    obc.boot()

    assert obc.mode == "NORMAL"
    assert obc.reboot_count == 0

    # Simulate software hang (infinite loop, no WDT kick)
    obc.freeze()

    # Advance time past WDT timeout (5.0s)
    # We step the simulation
    # We need to simulate time passage. obc.tick handles this.
    obc.tick(6.0)

    # Check that it rebooted
    assert obc.reboot_count == 1
    assert obc.mode == "SAFE_MODE"

    # Further checks: after reboot, it should be running (but in SAFE_MODE)
    # And watchdog should be cleared.
    assert obc.watchdog_timer == 0.0
    assert not obc.frozen
