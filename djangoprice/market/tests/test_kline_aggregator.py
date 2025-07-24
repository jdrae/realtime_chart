from django.test import TestCase

from market.models import Kline


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
        self._6m0s999ms = 1753173360999
        self._6m59s999ms = 1753173419999
        self._7m0s999ms = 1753173420999
        self._10m0s0ms = 1753173600000

    def test_fixture_loaded(self):
        self.assertGreater(Kline.objects.count(), 0)
