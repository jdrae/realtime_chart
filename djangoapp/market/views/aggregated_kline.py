from enums.interval import Interval
from market.models import AggregatedKline
from market.serializers.aggregated_kline import AggregatedKLineSerializer
from market.serializers.aggregated_kline_params import (
    AggregatedKLineListParamsSerializer,
    AggregatedKLineDetailParamsSerializer,
)
from rest_framework import serializers, status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView


class AggregatedKLineDetailView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        query_serializer = AggregatedKLineDetailParamsSerializer(data=request.query_params)
        try:
            query_serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        symbol = query_serializer.validated_data.get("symbol")
        interval = query_serializer.validated_data.get("interval")
        timestamp = query_serializer.validated_data.get("timestamp") * 1000

        queryset = AggregatedKline.objects.filter(
            symbol=symbol, interval=interval, start_time=timestamp
        ).get()
        serializer = AggregatedKLineSerializer(queryset)
        return Response(serializer.data)


class AggregatedKLineListView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        query_serializer = AggregatedKLineListParamsSerializer(data=request.query_params)
        try:
            query_serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        symbol = query_serializer.validated_data.get("symbol")
        interval = query_serializer.validated_data.get("interval")
        timestamp = query_serializer.validated_data.get("timestamp") * 1000
        limit = query_serializer.validated_data.get("limit")

        queryset = AggregatedKline.objects.filter(
            symbol=symbol, interval=interval, start_time__lte=timestamp
        ).order_by("-start_time")[:limit]
        serializer = AggregatedKLineSerializer(queryset, many=True)

        # check interval
        interval_seconds = Interval.from_label(interval).seconds
        last_sec = timestamp // 1000
        first_sec = last_sec - (interval_seconds * limit)
        ranges = list(range(last_sec, first_sec, -interval_seconds))

        filtered_data = []
        for aggregated_kline, times in zip(serializer.data, ranges):
            if aggregated_kline["start_time"] == (times * 1000):
                filtered_data.append(aggregated_kline)

        return Response(filtered_data)
