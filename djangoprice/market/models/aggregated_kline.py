from django.db import models


class AggregatedKline(models.Model):
    class Meta:
        _db = "market"
        db_table = "aggregated_kline"
        managed = True

    interval = models.CharField(max_length=10)
    symbol = models.CharField(max_length=20)
    start_time = models.BigIntegerField()
    end_time = models.BigIntegerField()
    row_count = models.IntegerField()

    open_price = models.DecimalField(max_digits=20, decimal_places=10)
    close_price = models.DecimalField(max_digits=20, decimal_places=10)
    high_price = models.DecimalField(max_digits=20, decimal_places=10)
    low_price = models.DecimalField(max_digits=20, decimal_places=10)

    trade_count = models.BigIntegerField()

    volume_base = models.DecimalField(max_digits=30, decimal_places=10)
    volume_quote = models.DecimalField(max_digits=30, decimal_places=10)

    taker_volume_base = models.DecimalField(max_digits=30, decimal_places=10)
    taker_volume_quote = models.DecimalField(max_digits=30, decimal_places=10)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("interval", "symbol", "start_time", "end_time")
