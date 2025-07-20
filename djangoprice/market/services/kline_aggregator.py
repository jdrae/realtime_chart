from datetime import timedelta, timezone, datetime

from config.config import SUPPORTED_SYMBOLS
from django.db.models import Count, Avg, Max, Min, Sum
from market.models.aggregated_kline import AggregatedKline
from market.models.kline import Kline


def get_interval_timedelta(interval: str) -> timedelta:
    if interval == "1m":
        return timedelta(minutes=1)
    elif interval == "5m":
        return timedelta(minutes=5)
    elif interval == "15m":
        return timedelta(minutes=15)
    else:
        raise ValueError(f"Unsupported interval: {interval}")


def get_time_range(interval: str, now):
    base_time = int(now.replace(second=0, microsecond=0).timestamp())
    start_ts = base_time - get_interval_timedelta(interval).seconds  # 0m 0s
    end_ts = start_ts + 59  # 0m 59s
    return start_ts * 1000, end_ts * 1000  # millisecond


def aggregate_all_symbols(interval: str, now):
    start_ts, end_ts = get_time_range(interval, now)

    for symbol in SUPPORTED_SYMBOLS:
        result = aggregate_kline_data(interval, symbol, start_ts, end_ts)
        if result is None:
            print(f"Warning: no data in {symbol}. interval: {interval}, time: {now})")
            continue
        insert_kline_data(result)


def aggregate_kline_data(interval: str, symbol: str, start_ts: int, end_ts: int):
    raw_qs = Kline.objects.filter(symbol=symbol, start_time__gte=start_ts, start_time__lte=end_ts)
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
        start_time=start_ts,
        end_time=end_ts,
        created_at=datetime.now(timezone.utc),
        **result,
    )


def insert_kline_data(instance: AggregatedKline):
    instance.save()
