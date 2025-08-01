from config import settings
from django.apps import AppConfig


class MarketConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "market"

    def ready(self):
        from django.utils.timezone import now
        from django_celery_beat.models import PeriodicTask, CrontabSchedule

        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute="*",
            hour="*",
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
            timezone=settings.CELERY_TIMEZONE,
        )

        PeriodicTask.objects.update_or_create(
            name="aggregate_1m",
            defaults={
                "task": "market.tasks.aggregate_1m",
                "crontab": schedule,
                "start_time": now(),
                "enabled": True,
            },
        )
