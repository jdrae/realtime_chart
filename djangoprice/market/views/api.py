from market.models.kline import Kline
from market.serializers.kline import KLineSerializer
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView


class KLineAPIView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request):
        symbol = request.query_params.get("symbol")
        utctime_ms = request.query_params.get("utctime")

        if not symbol or not utctime_ms:
            return Response(
                {"error": "Missing 'symbol' or 'utctime' parameter."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        symbol = symbol.upper()
        timestamp = int(int(utctime_ms) / 1000) * 1000
        queryset = Kline.objects.filter(symbol=symbol, start_time=timestamp).order_by("start_time")

        serializer = KLineSerializer(queryset, many=True)
        return Response(serializer.data)
