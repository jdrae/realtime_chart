from django.test import TestCase

from market.models.aggregated_kline import AggregatedKline
from market.models.kline import Kline
from market.services.kline_aggregator import aggregate_kline_data


class TestKlineAggregator(TestCase):
    databases = {"market"}

    def test_kline_aggregation(self):
        interval = "1m"
        symbol = "BTCUSDT"
        start_ts = 1752905760000
        end_ts = 1752905819000

        result = aggregate_kline_data(interval, symbol, start_ts, end_ts)

        if result:
            assert isinstance(result, AggregatedKline)
            assert result.symbol == symbol
            assert result.interval == interval
            assert result.row_count == 60
        else:
            assert result is None
