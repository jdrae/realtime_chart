import logging
from collections import defaultdict
from typing import List

import django
from django.db import transaction
from django.db.models import Count, Max, Min, Sum, QuerySet
from enums.interval import Interval
from market.models import CheckpointEnum
from market.models.aggregated_kline import AggregatedKline
from market.models.aggregated_kline_checkpoint import AggregatedKlineCheckpoint
from market.models.kline import Kline
from market.services.time_utils import get_interval_ranges, is_valid_range, ms_to_utctime

logger = logging.getLogger(__name__)


def get_pending_checkpoint(column_name):
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
        start_time_utc=ms_to_utctime(first_row.start_time),
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
        logger.warning(f"Duplicated kline data:{e}")


def update_checkpoint(interval, checkpoints: QuerySet, value: CheckpointEnum):
    if not checkpoints.exists():
        logger.error("Checkpoint and aggregated table are not consistent")
        return

    filter_kwargs = {Interval.from_label(interval).column: value}
    checkpoints.update(**filter_kwargs)


@transaction.atomic
def check_and_insert(interval, symbol, ranges) -> List[AggregatedKline]:
    # Iterate each range and check if it's valid and aggregate it.
    # Update checkpoint if checkpoint range is purely valid.
    # Log error if checkpoint range has not aggregated range and no data before it.
    inserted_data = []
    left_invalid_range_end_time = 0
    right_invalid_range_start_time = 0
    first_ms = ranges[0][0]
    last_ms = ranges[-1][1]

    # INSERT
    for start_ms, end_ms in ranges:
        if is_valid_range(interval, start_ms, end_ms):
            aggregated_kline = aggregate_kline_data(interval, symbol, start_ms, end_ms)
            if aggregated_kline:
                insert_kline_data(aggregated_kline)
                inserted_data.append(aggregated_kline)
            else:
                logger.error(
                    f"Checkpoint and raw table are not consistent. {symbol} [{ms_to_utctime(start_ms)}, {ms_to_utctime(end_ms)}]"
                )
        else:
            if len(inserted_data) == 0:  # update until first valid ranges
                left_invalid_range_end_time = end_ms
            if len(inserted_data) != 0:  # first invalid range after valid ranges
                right_invalid_range_start_time = start_ms
                break

    # UPDATE
    if len(inserted_data) != 0:
        checkpoints = AggregatedKlineCheckpoint.objects.filter(
            symbol=symbol, first_time__gte=first_ms, last_time__lte=last_ms
        )
        update_checkpoint(interval, checkpoints, CheckpointEnum.AGGREGATED)
        if left_invalid_range_end_time != 0:
            checkpoints = AggregatedKlineCheckpoint.objects.filter(
                symbol=symbol, first_time__gte=first_ms, first_time__lt=left_invalid_range_end_time
            )
            update_checkpoint(interval, checkpoints, CheckpointEnum.ERROR)
        if right_invalid_range_start_time != 0:
            checkpoints = AggregatedKlineCheckpoint.objects.filter(
                symbol=symbol, last_time__gt=right_invalid_range_start_time, last_time__lte=last_ms
            )
            update_checkpoint(interval, checkpoints, CheckpointEnum.PENDING)

    return inserted_data
