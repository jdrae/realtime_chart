from datetime import datetime, timezone

from celery import shared_task
from django.utils import timezone


@shared_task
def print_time():
    now_utc = datetime.now(timezone.utc)
    print(f"[UTC TIME] {now_utc.isoformat()}")
