from datetime import datetime

from celery import shared_task
from django.utils import timezone
from market.services.kline_aggregator import aggregate_all_symbols


@shared_task
def aggregate(interval):
    now = datetime.now(timezone.utc)

    aggregate_all_symbols(interval, now)
