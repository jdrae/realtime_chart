import time
from datetime import datetime, timedelta
from queue import Queue

from celery import shared_task
from config.config import SUPPORTED_SYMBOLS
from django.utils import timezone
from market.services.kline_aggregator import (
    check_last_data_close_time,
    aggregate_kline_data,
    insert_kline_data,
    check_and_insert,
)


@shared_task
def aggregate(interval):
    retry = 3
    wait = 3
    inserted_every_in_seconds = 61  # when data insertion is completed. data is inserted before this delta

    now = datetime.now(timezone.utc) - timedelta(seconds=inserted_every_in_seconds)
    queue = Queue()
    for symbol in SUPPORTED_SYMBOLS:
        queue.put(symbol)

    while not queue.empty():
        # iterate all symbols first
        qsize = queue.qsize()
        for _ in range(qsize):
            symbol = queue.get()
            is_done = check_and_insert(interval, symbol, now)
            if not is_done:
                print(f"Warning: no data in {symbol}. interval: {interval}, time: {now}).")
                queue.put(symbol)

        # sleep if left
        print(f"Sleeping {wait} seconds.")
        time.sleep(wait)
        retry -= 1
        if retry <= 0:
            break

    if queue.empty():
        print("Task successfully finished.")
        return True

    if retry <= 0:
        print("Warning: timeout exceeded.")
    else:  # symbols and timout left
        print("Error: Aggregation Failed with unexpected result.")
    return False
