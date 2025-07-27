from rest_framework import serializers

from enums.interval import Interval
from enums.symbol import Symbol


class KLineParamsSerializer(serializers.Serializer):
    symbol = serializers.ChoiceField(choices=[symbol.value for symbol in Symbol], required=True)
    timestamp = serializers.IntegerField(required=True)  # utc seconds
