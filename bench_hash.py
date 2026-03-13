import timeit

setup = """
from collections import deque
import time

history = {"ip": deque([time.time() - 0.5 for _ in range(50)])}
client_ip = "ip"
now = time.time()
period = 1.0
calls = 100
"""

test_current = """
while history[client_ip] and now - history[client_ip][0] >= period:
    history[client_ip].popleft()
if len(history[client_ip]) >= calls:
    pass
history[client_ip].append(now)
"""

test_optimized = """
client_history = history[client_ip]
while client_history and now - client_history[0] >= period:
    client_history.popleft()
if len(client_history) >= calls:
    pass
client_history.append(now)
"""

print("Current (Multiple Hash Lookups):", timeit.timeit(test_current, setup=setup, number=1000000))
print("Optimized (Local Variable):", timeit.timeit(test_optimized, setup=setup, number=1000000))
