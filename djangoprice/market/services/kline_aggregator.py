from collections import defaultdict
from datetime import timedelta, timezone, datetime

import django
from config.config import INTERVAL_COLUMNS
from django.core.exceptions import FieldError
from django.db.models import Count, Avg, Max, Min, Sum, QuerySet
from market.models.aggregated_kline import AggregatedKline
from market.models.aggregated_kline_checkpoint import AggregatedKlineCheckpoint
from market.models.kline import Kline


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


def is_valid_range(interval, start_ms, end_ms):
    # round millisecond and check if range is valid
    start_sec = int(datetime.fromtimestamp(ms_to_sec(start_ms)).replace(second=0).timestamp())
    end_sec = start_sec + get_interval_seconds(interval)
    return start_sec == ms_to_sec(start_ms) and end_sec == ms_to_sec(end_ms)


def get_interval_ranges(interval: str, first_ms: int, last_ms: int) -> list:
    interval_seconds = get_interval_seconds(interval)

    result = []
    start_sec = (ms_to_sec(first_ms) // interval_seconds) * interval_seconds
    for i in range(start_sec, ms_to_sec(last_ms), interval_seconds):
        result.append([sec_to_ms(i), sec_to_ms(i + interval_seconds)])

    result[0][0] = first_ms
    result[-1][1] = last_ms
    return result


def get_not_aggregated_checkpoint(column_name):
    if column_name not in INTERVAL_COLUMNS:
        raise FieldError(f"'{column_name}' is not a valid interval column")

    filter_kwargs = {column_name: False}
    return AggregatedKlineCheckpoint.objects.filter(**filter_kwargs)


def arrange_checkpoint(queryset: QuerySet[AggregatedKlineCheckpoint], interval: str) -> dict:
    state = defaultdict(list)
    for checkpoint in queryset:
        state[checkpoint.symbol].append(checkpoint.first_time)
        state[checkpoint.symbol].append(checkpoint.last_time)

    result = defaultdict(list)
    for symbol, times in state.items():
        first_ms = min(times)
        last_ms = max(times)
        time_ranges = get_interval_ranges(interval, first_ms, last_ms)  # ordered
        result[symbol] = time_ranges

    return result


def aggregate_kline_data(interval: str, symbol: str, start_ms: int, end_ms: int):
    raw_qs = Kline.objects.filter(symbol=symbol, start_time__gte=start_ms, end_time__lte=end_ms)
    if not raw_qs.exists():
        return None

    result = raw_qs.aggregate(
        row_count=Count("id"),
        open_price=Avg("open_price"),
        close_price=Avg("close_price"),
        high_price=Max("high_price"),
        low_price=Min("low_price"),
        trade_count=Sum("trade_count"),
        volume_base=Sum("volume_base"),
        volume_quote=Sum("volume_quote"),
        taker_volume_base=Sum("taker_volume_base"),
        taker_volume_quote=Sum("taker_volume_quote"),
    )

    return AggregatedKline(
        interval=interval,
        symbol=symbol,
        start_time=start_ms,
        end_time=end_ms,
        created_at=datetime.now(timezone.utc),
        **result,
    )


def insert_kline_data(instance: AggregatedKline):
    try:
        instance.save()
    except django.db.utils.IntegrityError as e:
        print(f"Warning: duplicated kline data:{e}")


def check_and_insert(interval: str, symbol: str, ranges: list):

    for start_ms, end_ms in ranges:
        if is_valid_range(interval, start_ms, end_ms):
            result = aggregate_kline_data(interval, symbol, start_ms, end_ms)
            if result:
                insert_kline_data(result)
            else:
                print("Error: Checkpoint and raw table are not consistent.")
