from django.test import TestCase

from market.models.kline import Kline
from market.models.aggregated_kline import AggregatedKline
from market.services import kline_aggregator
from datetime import datetime, timezone


class TestKlineAggregator(TestCase):
    databases = {"default", "market"}
    fixtures = ["market/fixtures/kline_1s.json"]

    @classmethod
    def setUpTestData(cls):
        count = Kline.objects.count()
        print(f"Loaded Kline fixture: {count} rows")


    def test_fixture_loaded(self):
        self.assertGreater(Kline.objects.count(), 0)


    def test_get_time_range(self):
        now = datetime.fromtimestamp(1752905823, tz=timezone.utc)
        interval = "1m"

        start_ts, end_ts = kline_aggregator.get_time_range(interval, now)

        expected_start = int(now.replace(second=0, microsecond=0).timestamp()) - 60
        expected_start *= 1000
        expected_end = expected_start + 59 * 1000
        self.assertEqual(start_ts, expected_start)
        self.assertEqual(end_ts, expected_end)


    def test_aggregate_kline_data(self):
        kline = Kline.objects.order_by('-id').first()
        now = datetime.fromtimestamp(int(kline.event_time) // 1000, tz=timezone.utc)
        symbol = kline.symbol
        interval = "1m"

        start_ts, end_ts = kline_aggregator.get_time_range(interval, now)
        result = kline_aggregator.aggregate_kline_data(interval, symbol, start_ts, end_ts)

        self.assertIsNotNone(result)
        self.assertEqual(result.symbol, symbol)
        self.assertEqual(result.interval, interval)
        self.assertEqual(result.start_time, start_ts)
        self.assertEqual(result.end_time, end_ts)
        self.assertGreater(result.row_count, 0)


    def test_insert_kline_data(self):
        kline = Kline.objects.order_by('-id').first()
        now = datetime.fromtimestamp(int(kline.event_time) // 1000, tz=timezone.utc)
        symbol = kline.symbol
        interval = "1m"
        AggregatedKline.objects.all().delete()

        start_ts, end_ts = kline_aggregator.get_time_range(interval, now)
        result = kline_aggregator.aggregate_kline_data(interval, symbol, start_ts, end_ts)
        kline_aggregator.insert_kline_data(result)

        self.assertEqual(AggregatedKline.objects.count(), 1)
        agg = AggregatedKline.objects.first()
        self.assertEqual(agg.symbol, symbol)
        self.assertEqual(agg.interval, interval)


    def test_aggregate_all_symbols(self):
        kline = Kline.objects.order_by('-id').first()
        now = datetime.fromtimestamp(int(kline.event_time) // 1000, tz=timezone.utc)
        interval = "1m"
        AggregatedKline.objects.all().delete()

        kline_aggregator.aggregate_all_symbols(interval, now)
        
        symbols = set(AggregatedKline.objects.values_list("symbol", flat=True))
        self.assertIn("BTCUSDT", symbols)
        self.assertEqual(AggregatedKline.objects.filter(symbol="BTCUSDT").count(), 1)
