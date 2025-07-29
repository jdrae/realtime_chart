from rest_framework import serializers, status

from market.models import AggregatedKline
from market.serializers.aggregated_kline import AggregatedKLineSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from market.serializers.aggregated_kline_params import AggregatedKLineParamsSerializer


class AggregatedKLineListView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        query_serializer = AggregatedKLineParamsSerializer(data=request.query_params)
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
        return Response(serializer.data)
