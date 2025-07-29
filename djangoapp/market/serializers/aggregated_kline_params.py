from rest_framework import serializers

from enums.interval import Interval
from enums.symbol import Symbol


class AggregatedKLineParamsSerializer(serializers.Serializer):
    symbol = serializers.ChoiceField(choices=[symbol.value for symbol in Symbol], required=True)
    interval = serializers.ChoiceField(choices=[interval.label for interval in Interval], required=True)
    timestamp = serializers.IntegerField(required=True)  # utc seconds
    limit = serializers.IntegerField(required=True, max_value=30)
