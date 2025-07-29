from config.settings import TRUE_IF_TEST_ELSE_FALSE
from django.db import models


class Indicator(models.Model):
    class Meta:
        db_table = "indicator"
        unique_together = ("symbol", "interval", "start_time", "label")
        managed = TRUE_IF_TEST_ELSE_FALSE

    symbol = models.CharField(max_length=20)
    interval = models.CharField(max_length=10)
    start_time = models.BigIntegerField()

    label = models.CharField(max_length=20)
    value = models.DecimalField(max_digits=20, decimal_places=10)

    created_at = models.DateTimeField(auto_now_add=True)
