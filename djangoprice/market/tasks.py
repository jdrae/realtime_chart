import time

from celery import shared_task
from market.services.kline_aggregator import (
    get_pending_checkpoint,
    arrange_checkpoint,
    check_and_insert,
)
from market.services.time_utils import get_interval_columns


@shared_task
def aggregate_1m():
    print("Starting task aggregate_1m")
    interval = "1m"
    target_column = get_interval_columns(interval)
    retries = 3
    wait_sec = 5

    while retries:
        time.sleep(wait_sec)
        retries -= 1
        checkpoints = get_pending_checkpoint(target_column)
        if len(checkpoints) == 0:  # until all checkpoints are handled
            print("All checkpoints handled in aggregate_1m")
            break
        arranged_checkpoints = arrange_checkpoint(interval, checkpoints)
        for symbol, ranges in arranged_checkpoints.items():
            check_and_insert(interval, symbol, ranges)
