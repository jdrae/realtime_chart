from collections import defaultdict

import django
from config.config import INTERVAL_COLUMNS
from django.core.exceptions import FieldError
from django.db.models import Count, Max, Min, Sum, QuerySet
from market.models import CheckpointEnum
from market.models.aggregated_kline import AggregatedKline
from market.models.aggregated_kline_checkpoint import AggregatedKlineCheckpoint
from market.models.kline import Kline
from market.services.time_utils import get_interval_ranges, is_valid_range, get_interval_columns


def get_pending_checkpoint(column_name):
    if column_name not in INTERVAL_COLUMNS:
        raise FieldError(f"'{column_name}' is not a valid interval column")

    filter_kwargs = {column_name: CheckpointEnum.PENDING}
    return AggregatedKlineCheckpoint.objects.filter(**filter_kwargs)


def arrange_checkpoint(interval, queryset: QuerySet[AggregatedKlineCheckpoint]) -> dict:
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


def aggregate_kline_data(interval, symbol, start_ms, end_ms):
    raw_qs = Kline.objects.filter(symbol=symbol, start_time__gte=start_ms, close_time__lt=end_ms).order_by(
        "start_time"
    )
    if not raw_qs.exists():
        print("Warning: No data for symbol", symbol)
        return None

    first_row = raw_qs.first()
    last_row = raw_qs.last()

    result = raw_qs.aggregate(
        row_count=Count("id"),
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
        start_time=first_row.start_time,
        close_time=last_row.close_time,
        open_price=first_row.open_price,
        close_price=last_row.close_price,
        **result,
    )


def insert_kline_data(instance: AggregatedKline):
    try:
        instance.save()
    except django.db.utils.IntegrityError as e:
        print(f"Warning: duplicated kline data:{e}")


def update_checkpoint(interval, symbol, first_ms, last_ms, value):
    if first_ms > last_ms or first_ms == 0 or last_ms == 0:
        return
    checkpoints = AggregatedKlineCheckpoint.objects.filter(
        symbol=symbol, first_time__gte=first_ms, last_time__lte=last_ms
    )
    if not checkpoints.exists():
        print("Error: Checkpoint and aggregated table are not consistent")

    filter_kwargs = {get_interval_columns(interval): value}
    checkpoints.update(**filter_kwargs)


def check_and_insert(interval, symbol, ranges):
    successful_insert = 0
    first_ms = ranges[0][0]
    valid_ms_list = []

    for start_ms, end_ms in ranges:
        if is_valid_range(interval, start_ms, end_ms):
            aggregated_kline = aggregate_kline_data(interval, symbol, start_ms, end_ms)
            if aggregated_kline:
                insert_kline_data(aggregated_kline)
                valid_ms_list.append(aggregated_kline.start_time)
                valid_ms_list.append(aggregated_kline.close_time)
                successful_insert += 1
            else:
                print(f"Error: Checkpoint and raw table are not consistent. {symbol} [{start_ms}, {end_ms}]")
        else:
            print(f"Warning: Invalid range: {symbol} [{start_ms}, {end_ms}]")

    if valid_ms_list:
        first_valid_ms = min(valid_ms_list)
        last_valid_ms = max(valid_ms_list)
        update_checkpoint(interval, symbol, first_ms, first_valid_ms, value=CheckpointEnum.ERROR)
        update_checkpoint(interval, symbol, first_valid_ms, last_valid_ms, value=CheckpointEnum.AGGREGATED)
    return successful_insert  # for test
