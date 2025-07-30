from market.models import AggregatedKline
from rest_framework import serializers


class AggregatedKLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = AggregatedKline
        fields = [
            "id",
            "interval",
            "symbol",
            "start_time_utc",
            "start_time",
            "close_time",
            "open_price",
            "close_price",
            "high_price",
            "low_price",
            "trade_count",
            "volume_base",
            "volume_quote",
            "taker_volume_base",
            "taker_volume_quote",
            "created_at",
        ]
