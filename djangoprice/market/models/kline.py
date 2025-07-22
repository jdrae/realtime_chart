from django.db import models

from config.settings import TRUE_IF_TEST_ELSE_FALSE


class Kline(models.Model):
    class Meta:
        db_table = "kline_1s_processed"
        managed = TRUE_IF_TEST_ELSE_FALSE

    id = models.BigAutoField(primary_key=True)

    event_time = models.BigIntegerField()
    symbol = models.CharField(max_length=20)
    is_closed = models.BooleanField()

    start_time = models.BigIntegerField()
    close_time = models.BigIntegerField()

    first_trade_id = models.BigIntegerField()
    last_trade_id = models.BigIntegerField()

    open_price = models.DecimalField(max_digits=20, decimal_places=10)
    close_price = models.DecimalField(max_digits=20, decimal_places=10)
    high_price = models.DecimalField(max_digits=20, decimal_places=10)
    low_price = models.DecimalField(max_digits=20, decimal_places=10)

    trade_count = models.BigIntegerField()

    volume_base = models.DecimalField(max_digits=30, decimal_places=10)
    volume_quote = models.DecimalField(max_digits=30, decimal_places=10)

    taker_volume_base = models.DecimalField(max_digits=30, decimal_places=10)
    taker_volume_quote = models.DecimalField(max_digits=30, decimal_places=10)

    created_at = models.DateTimeField()
