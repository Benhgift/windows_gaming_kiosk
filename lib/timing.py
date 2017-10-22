import time
from box import Box


def init_timins():
    return Box({
        'current_time': time.time(),
        'last_time_idle': current_time,
        'last_time_swapped': current_time,
    })
