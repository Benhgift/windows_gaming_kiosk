import time
from box import Box


def init_timings():
    return Box({
        'current_time': time.time(),
        'last_time_idle': time.time(),
        'last_time_swapped': time.time(),
    })


def time_to_swap_games(timings):
    been_8_hours_since_change = timings.current_time - timings.last_time_swapped > 60 * 60 * 8
    been_20_mins_since_idle = timings.current_time - timings.last_time_idle > 60 * 20
    between_3_and_5am = 3 < time.localtime().tm_hour < 5
    return been_8_hours_since_change and between_3_and_5am and been_1_min_since_idle

