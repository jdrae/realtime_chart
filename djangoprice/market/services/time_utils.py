from datetime import timedelta

from enums.interval import Interval


def ms_to_sec(ms: int) -> int:
    return round(ms / 1000)


def sec_to_ms(sec: int) -> int:
    return sec * 1000


def get_interval_ranges(interval: str, first_ms: int, last_ms: int) -> list:
    # Split given time range(from first_ms to last_ms) into interval window,
    # considering each split should start and end with seconds=0, milliseconds=0.
    # Lastly, modify start time point to first_ms and last time point to last_ms.
    # ! Be careful that milliseconds are rounded to prevent overflow and optimize calculation.
    interval_seconds = Interval.from_label(interval).seconds

    result = []
    start_sec = (ms_to_sec(first_ms) // interval_seconds) * interval_seconds
    for i in range(start_sec, ms_to_sec(last_ms), interval_seconds):
        result.append([sec_to_ms(i), sec_to_ms(i + interval_seconds)])

    if result:  # result is none if difference between first_ms and last_ms is less than 1s
        result[0][0] = first_ms
        result[-1][1] = last_ms
    return result


def is_valid_range(interval, start_ms, end_ms):
    # Round millisecond and check if range is valid.
    # Difference of valid range should same with interval seconds.
    start_sec = ms_to_sec(start_ms)
    end_sec = start_sec + Interval.from_label(interval).seconds
    return start_sec == ms_to_sec(start_ms) and end_sec == ms_to_sec(end_ms)
