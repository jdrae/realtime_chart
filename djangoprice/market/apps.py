from django.apps import AppConfig


class MarketConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "market"

    def ready(self):
        from django_celery_beat.models import PeriodicTask, CrontabSchedule
        from django.utils.timezone import now

        schedule, created = CrontabSchedule.objects.get_or_create(minute='*')

        PeriodicTask.objects.update_or_create(
            name='print_time',
            defaults={
                'task': 'market.tasks.print_time',
                'crontab': schedule,
                'start_time': now(),
                'enabled': True,
            }
        )