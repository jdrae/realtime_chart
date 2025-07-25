from django.test import TestCase

from market.services.time_utils import ms_to_sec, get_interval_ranges, is_valid_range


class TestKlineAggregator(TestCase):
    def setUp(self):
        self._5m0s0ms = 1753173300000
        self._5m0s1ms = 1753173300001
        self._5m59s0ms = 1753173359000
        self._5m59s999ms = 1753173359999
        self._6m0s0ms = 1753173360000
        self._6m0s999ms = 1753173360999
        self._6m59s999ms = 1753173419999
        self._7m0s999ms = 1753173420999
        self._10m0s0ms = 1753173600000

    def test_ms_to_sec_1(self):
        _5m59s = 1753173359
        self.assertEqual(ms_to_sec(self._5m59s0ms), _5m59s)

    def test_ms_to_sec_2(self):
        _6m0s = 1753173360
        self.assertEqual(ms_to_sec(self._5m59s999ms), _6m0s)

    def test_get_interval_ranges_1(self):
        interval = "1m"
        start_ms = self._5m0s0ms
        end_ms = self._5m59s999ms

        result = get_interval_ranges(interval, start_ms, end_ms)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], start_ms)
        self.assertEqual(result[-1][1], end_ms)

    def test_get_interval_ranges_2(self):
        interval = "1m"
        start_ms = self._5m0s0ms
        end_ms = self._6m0s0ms

        result = get_interval_ranges(interval, start_ms, end_ms)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], start_ms)
        self.assertEqual(result[-1][1], end_ms)

    def test_get_interval_ranges_3(self):
        interval = "1m"
        start_ms = self._5m0s0ms
        end_ms = self._6m0s999ms

        result = get_interval_ranges(interval, start_ms, end_ms)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], start_ms)
        self.assertEqual(result[-1][1], end_ms)

    def test_get_interval_ranges_4(self):
        interval = "1m"
        start_ms = self._5m0s0ms
        end_ms = self._5m0s1ms

        result = get_interval_ranges(interval, start_ms, end_ms)

        self.assertEqual(len(result), 0)

    def test_get_interval_ranges_5(self):
        interval = "1m"
        start_ms = self._5m0s1ms
        end_ms = self._6m59s999ms

        result = get_interval_ranges(interval, start_ms, end_ms)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], start_ms)
        self.assertEqual(result[-1][1], end_ms)

    def test_get_interval_ranges_6(self):
        interval = "1m"
        start_ms = self._5m0s0ms
        end_ms = self._7m0s999ms

        result = get_interval_ranges(interval, start_ms, end_ms)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0][0], start_ms)
        self.assertEqual(result[-1][1], end_ms)

    def test_get_interval_ranges_7(self):
        interval = "5m"
        start_ms = self._5m0s0ms
        end_ms = self._7m0s999ms

        result = get_interval_ranges(interval, start_ms, end_ms)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], start_ms)
        self.assertEqual(result[-1][1], end_ms)

    def test_get_interval_ranges_8(self):
        interval = "5m"
        start_ms = self._5m0s0ms
        end_ms = self._10m0s0ms

        result = get_interval_ranges(interval, start_ms, end_ms)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][0], start_ms)
        self.assertEqual(result[-1][1], end_ms)

    def test_is_valid_range_1(self):
        interval = "1m"
        start_ms = self._5m0s0ms
        end_ms = self._5m59s999ms

        self.assertTrue(is_valid_range(interval, start_ms, end_ms))

    def test_is_valid_range_2(self):
        interval = "1m"
        start_ms = self._5m0s0ms
        end_ms = self._6m0s0ms

        self.assertTrue(is_valid_range(interval, start_ms, end_ms))

    def test_is_valid_range_3(self):
        interval = "1m"
        start_ms = self._6m0s0ms
        end_ms = self._6m0s999ms

        self.assertFalse(is_valid_range(interval, start_ms, end_ms))

    def test_is_valid_range_4(self):
        interval = "1m"
        start_ms = self._5m0s0ms
        end_ms = self._5m0s1ms

        self.assertFalse(is_valid_range(interval, start_ms, end_ms))

    def test_is_valid_range_5(self):
        interval = "1m"
        start_ms = self._5m0s0ms
        end_ms = self._6m59s999ms

        self.assertFalse(is_valid_range(interval, start_ms, end_ms))

    def test_is_valid_range_6(self):
        interval = "1m"
        start_ms = self._5m0s1ms
        end_ms = self._5m59s999ms

        self.assertTrue(is_valid_range(interval, start_ms, end_ms))

    def test_is_valid_range_7(self):
        interval = "1m"
        start_ms = self._6m0s999ms
        end_ms = self._6m59s999ms

        self.assertFalse(is_valid_range(interval, start_ms, end_ms))

    def test_is_valid_range_8(self):
        interval = "1m"
        start_ms = self._5m0s0ms
        end_ms = self._5m59s0ms

        self.assertFalse(is_valid_range(interval, start_ms, end_ms))

    def test_is_valid_range_9(self):
        interval = "5m"
        start_ms = self._5m0s0ms
        end_ms = self._10m0s0ms

        self.assertTrue(is_valid_range(interval, start_ms, end_ms))

    def test_is_valid_range_10(self):
        interval = "5m"
        start_ms = self._6m59s999ms
        end_ms = self._10m0s0ms

        self.assertFalse(is_valid_range(interval, start_ms, end_ms))
