from datetime import datetime, timezone

from enums.interval import Interval
from enums.symbol import Symbol
from rest_framework import serializers


class TimestampValidationMixin(serializers.Serializer):
    def validate_timestamp(self, value):
        value = int(value)
        try:
            datetime.fromtimestamp(value, tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            raise serializers.ValidationError("timestamp is not a valid UTC seconds timestamp.")
        return value


class AggregatedKLineDetailParamsSerializer(TimestampValidationMixin):
    symbol = serializers.ChoiceField(choices=[symbol.value for symbol in Symbol], required=True)
    interval = serializers.ChoiceField(choices=[interval.label for interval in Interval], required=True)
    timestamp = serializers.IntegerField(required=True)  # utc seconds


class AggregatedKLineListParamsSerializer(TimestampValidationMixin):
    symbol = serializers.ChoiceField(choices=[symbol.value for symbol in Symbol], required=True)
    interval = serializers.ChoiceField(choices=[interval.label for interval in Interval], required=True)
    timestamp = serializers.IntegerField(required=True)  # utc seconds
    limit = serializers.IntegerField(required=True, max_value=30)
