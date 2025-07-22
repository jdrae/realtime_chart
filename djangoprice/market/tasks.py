import time

from celery import shared_task
from config.config import SUPPORTED_SYMBOLS
from market.services.kline_aggregator import (
    get_not_aggregated_checkpoint,
    arrange_checkpoint,
    check_and_insert,
)


@shared_task
def aggregate_1m():
    interval = "1m"
    target_column = "is_1m_aggregated"
    retries = 3
    wait_sec = 5

    while retries:
        retries -= 1
        checkpoints = get_not_aggregated_checkpoint(target_column)
        if len(checkpoints) == 0:
            break
        arranged_checkpoints = arrange_checkpoint(checkpoints, interval)
        for symbol, ranges in arranged_checkpoints.items():
            result = check_and_insert(interval, symbol, ranges)
        time.sleep(wait_sec)
