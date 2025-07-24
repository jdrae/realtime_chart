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
    interval = "1m"
    target_column = get_interval_columns(interval)
    retries = 3
    wait_sec = 5

    while retries:
        time.sleep(wait_sec)
        print(f"Retry time left: {retries}")
        retries -= 1
        checkpoints = get_pending_checkpoint(target_column)
        print(f"Checkpoints: {len(checkpoints)}")
        if len(checkpoints) == 0:  # until all checkpoints are handled
            print("All checkpoints handled")
            break
        arranged_checkpoints = arrange_checkpoint(interval, checkpoints)
        print(f"Arranged checkpoints: {len(arranged_checkpoints)}")
        for symbol, ranges in arranged_checkpoints.items():
            print(f"Checkpoint: {symbol}, ranges: {len(ranges)}, example: {ranges[0]}")
            check_and_insert(interval, symbol, ranges)
