from django.test import TestCase
from market.models.aggregated_kline import AggregatedKline
from market.models.kline import Kline
from market.services import kline_aggregator
from market.services.kline_aggregator import sec_to_ms, ms_to_sec, is_valid_range, get_interval_ranges


class TestKlineAggregator(TestCase):
    databases = {"default", "market"}
    fixtures = ["market/fixtures/kline_1s.json"]

    @classmethod
    def setUpTestData(cls):
        count = Kline.objects.count()
        print(f"Loaded Kline fixture: {count} rows")

    def setUp(self):
        self._5m0s0ms = 1753173300000
        self._5m0s1ms = 1753173300001
        self._5m59s0ms = 1753173359000
        self._5m59s999ms = 1753173359999
        self._6m0s0ms = 1753173360000
        self._6m59s999ms = 1753173419999
        self._7m0s999ms = 1753173420999

    def test_fixture_loaded(self):
        self.assertGreater(Kline.objects.count(), 0)

    def test_is_valid_range_true(self):
        interval = "1m"
        start_ms = self._5m0s0ms
        end_ms = self._5m59s999ms

        self.assertTrue(is_valid_range(interval, start_ms, end_ms))

    def test_is_valid_range_false(self):
        interval = "1m"
        start_ms = self._5m0s0ms
        end_ms = self._5m59s0ms

        self.assertFalse(is_valid_range(interval, start_ms, end_ms))

    def test_get_interval_ranges(self):
        interval = "1m"
        start_ms = self._5m0s0ms
        end_ms = self._6m59s999ms

        result = get_interval_ranges(interval, start_ms, end_ms)
        print(result)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], start_ms)
        self.assertEqual(result[-1][1], end_ms)

    def test_get_interval_ranges_end(self):
        interval = "1m"
        start_ms = self._5m0s0ms
        end_ms = self._7m0s999ms

        result = get_interval_ranges(interval, start_ms, end_ms)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0][0], start_ms)
        self.assertEqual(result[-1][1], end_ms)
