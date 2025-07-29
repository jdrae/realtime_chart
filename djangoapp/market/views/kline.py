from rest_framework import serializers, status

from market.models.kline import Kline
from market.serializers.kline import KLineSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from market.serializers.kline_params import KLineParamsSerializer


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

        queryset = Kline.objects.filter(symbol=symbol, start_time=timestamp).get()

        serializer = KLineSerializer(queryset)
        return Response(serializer.data)
