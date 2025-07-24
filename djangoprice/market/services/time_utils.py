from datetime import timedelta


def ms_to_sec(ms: int) -> int:
    return round(ms / 1000)


def sec_to_ms(sec: int) -> int:
    return sec * 1000


def get_interval_seconds(interval: str) -> int:
    if interval == "1m":
        return timedelta(minutes=1).seconds
    elif interval == "5m":
        return timedelta(minutes=5).seconds
    elif interval == "15m":
        return timedelta(minutes=15).seconds
    else:
        raise ValueError(f"Unsupported interval: {interval}")


def get_interval_columns(interval: str):
    if interval == "1m":
        return "is_1m_aggregated"
    elif interval == "5m":
        return "is_5m_aggregated"
    elif interval == "15m":
        return "is_15m_aggregated"
    else:
        raise ValueError(f"Unsupported interval: {interval}")


def get_interval_ranges(interval: str, first_ms: int, last_ms: int) -> list:
    # Split given time range(from first_ms to last_ms) into interval window,
    # considering each split should start and end with seconds=0, milliseconds=0.
    # Lastly, modify start time point to first_ms and last time point to last_ms.
    # ! Be careful that milliseconds are rounded to prevent overflow and optimize calculation.
    interval_seconds = get_interval_seconds(interval)

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
    end_sec = start_sec + get_interval_seconds(interval)
    return start_sec == ms_to_sec(start_ms) and end_sec == ms_to_sec(end_ms)
