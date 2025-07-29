from config.settings import TRUE_IF_TEST_ELSE_FALSE
from django.db import models

from market.models.checkpoint_enum import CheckpointEnum


class AggregatedKlineCheckpoint(models.Model):
    class Meta:
        db_table = "aggregated_kline_checkpoint"
        unique_together = ("symbol", "first_time", "last_time")
        managed = TRUE_IF_TEST_ELSE_FALSE

    symbol = models.CharField(max_length=10)
    first_time = models.BigIntegerField()
    last_time = models.BigIntegerField()

    is_1m_aggregated = models.SmallIntegerField(choices=CheckpointEnum.choices)
    is_5m_aggregated = models.SmallIntegerField(choices=CheckpointEnum.choices)
    is_15m_aggregated = models.SmallIntegerField(choices=CheckpointEnum.choices)

    created_at = models.DateTimeField()
