from django.test import TestCase

from market.models.kline import Kline


class TestKlineAggregator(TestCase):
    databases = {"default", "market"}

    def test_get_kline_data(self):
        symbol = "BTCUSDT"
        result = Kline.objects.filter(symbol=symbol)
        if result:
            assert isinstance(result, Kline)
            assert result.symbol == symbol
