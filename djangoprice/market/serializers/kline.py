from market.models.kline import Kline
from rest_framework import serializers


class KLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kline
        fields = [
            "id",
            "event_time",
            "symbol",
            "is_closed",
            "start_time",
            "close_time",
            "first_trade_id",
            "last_trade_id",
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
