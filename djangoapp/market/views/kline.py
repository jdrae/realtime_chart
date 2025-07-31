from django.shortcuts import get_object_or_404
from market.models.kline import Kline
from market.serializers.kline import KLineSerializer
from market.serializers.kline_params import KLineParamsSerializer
from rest_framework import serializers, status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView


class KLineView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        query_serializer = KLineParamsSerializer(data=request.query_params)
        try:
            query_serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        symbol = query_serializer.validated_data.get("symbol")
        timestamp = query_serializer.validated_data.get("timestamp") * 1000

        queryset = get_object_or_404(Kline, symbol=symbol, start_time=timestamp)

        serializer = KLineSerializer(queryset)
        return Response(serializer.data)
