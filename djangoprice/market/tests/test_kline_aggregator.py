from django.test import TestCase
from market.models import Kline, AggregatedKlineCheckpoint, AggregatedKline, CheckpointEnum
from market.services.kline_aggregator import (
    get_pending_checkpoint,
    arrange_checkpoint,
    aggregate_kline_data,
    insert_kline_data,
    check_and_insert,
    update_checkpoint,
)


class TestKlineAggregator(TestCase):
    databases = {"default", "market"}
    fixtures = ["market/fixtures/kline_1s_processed.json", "market/fixtures/aggregated_kline_checkpoint.json"]

    @classmethod
    def setUpTestData(cls):
        count = Kline.objects.count()
        print(f"Loaded Kline fixture: {count} rows")
        count = AggregatedKlineCheckpoint.objects.count()
        print(f"Loaded AggregatedKlineCheckpoint fixture: {count} rows")

    def setUp(self):
        self.checkpoint_start_ms = 1753325942000  # 02:59:02.000
        self.checkpoint_end_ms = 1753326345999  # 03:05:45.999
        self.total_1m_ranges = 7
        self.valid_1m_ranges = 5
        self.total_5m_ranges = 3
        self.valid_5m_ranges = 1
        self.n_symbols = 2

    def test_fixture_loaded(self):
        self.assertGreater(Kline.objects.count(), 0)

    def test_get_not_aggregated_checkpoint(self):
        expected = AggregatedKlineCheckpoint.objects.all()

        qs = get_pending_checkpoint("is_1m_aggregated")

        self.assertEqual(qs.count(), len(expected))

    def test_arrange_checkpoint_1m(self):
        qs = get_pending_checkpoint("is_1m_aggregated")
        arranged_checkpoints = arrange_checkpoint("1m", qs)
        self.assertEqual(len(arranged_checkpoints.keys()), self.n_symbols)
        self.assertEqual(len(arranged_checkpoints["ETHUSDT"]), self.total_1m_ranges)
        self.assertEqual(len(arranged_checkpoints["BTCUSDT"]), self.total_1m_ranges)
        self.assertEqual(arranged_checkpoints["ETHUSDT"][0][0], self.checkpoint_start_ms)
        self.assertEqual(arranged_checkpoints["ETHUSDT"][-1][1], self.checkpoint_end_ms)

    def test_arrange_checkpoint_5m(self):
        qs = get_pending_checkpoint("is_5m_aggregated")
        arranged_checkpoints = arrange_checkpoint("5m", qs)

        self.assertEqual(len(arranged_checkpoints.keys()), self.n_symbols)
        self.assertEqual(len(arranged_checkpoints["ETHUSDT"]), self.total_5m_ranges)
        self.assertEqual(len(arranged_checkpoints["BTCUSDT"]), self.total_5m_ranges)
        self.assertEqual(arranged_checkpoints["ETHUSDT"][0][0], self.checkpoint_start_ms)
        self.assertEqual(arranged_checkpoints["ETHUSDT"][-1][1], self.checkpoint_end_ms)

    def test_aggregated_kline_data(self):
        interval = "1m"
        symbol = "BTCUSDT"
        start_ms = 1753326000000
        end_ms = 1753326060000

        aggregated_kline = aggregate_kline_data(interval, symbol, start_ms, end_ms)
        self.assertIsNotNone(aggregated_kline)
        self.assertIsNone(aggregated_kline.pk)  # not saved
        self.assertEqual(AggregatedKline.objects.count(), 0)  # not saved
        self.assertEqual(aggregated_kline.start_time, start_ms)
        self.assertLess(aggregated_kline.close_time, end_ms)  # note

    def test_insert_kline_data(self):
        interval = "1m"
        symbol = "ETHUSDT"
        start_ms = 1753326000000
        end_ms = 1753326060000

        aggregated_kline = aggregate_kline_data(interval, symbol, start_ms, end_ms)
        insert_kline_data(aggregated_kline)
        saved_instance = AggregatedKline.objects.first()

        self.assertEqual(AggregatedKline.objects.count(), 1)
        self.assertIsNotNone(saved_instance.pk)
        self.assertEqual(saved_instance.symbol, symbol)
        self.assertEqual(saved_instance.interval, interval)

    def test_update_checkpoint(self):
        interval = "1m"
        symbol = "ETHUSDT"
        start_ms = 1753326000000
        end_ms = 1753326060000

        checkpoints = AggregatedKlineCheckpoint.objects.filter(
            symbol=symbol, first_time__gte=start_ms, last_time__lte=end_ms
        )
        update_checkpoint(interval, checkpoints, CheckpointEnum.AGGREGATED)

        for checkpoint in checkpoints:
            self.assertEqual(checkpoint.is_1m_aggregated, CheckpointEnum.AGGREGATED)

    def test_check_and_insert_1m(self):
        interval = "1m"
        qs = get_pending_checkpoint("is_1m_aggregated")
        arranged_checkpoints = arrange_checkpoint(interval, qs)
        symbol = "BTCUSDT"
        left_invalid_range_end_time = 1753326000000
        valid_range_start_time = 1753326000000
        valid_range_end_time = 1753326300000
        right_invalid_range_start_time = 1753326300000

        successful_insert = check_and_insert(interval, symbol, arranged_checkpoints[symbol])
        self.assertEqual(successful_insert, self.valid_1m_ranges)

        # Aggregated
        checkpoints = AggregatedKlineCheckpoint.objects.filter(
            symbol=symbol, first_time__gte=valid_range_start_time, last_time__lte=valid_range_end_time
        )
        for checkpoint in checkpoints:
            self.assertEqual(checkpoint.is_1m_aggregated, CheckpointEnum.AGGREGATED)

        # Error
        checkpoints = AggregatedKlineCheckpoint.objects.filter(
            symbol=symbol, first_time__lt=left_invalid_range_end_time
        )
        for checkpoint in checkpoints:
            self.assertEqual(checkpoint.is_1m_aggregated, CheckpointEnum.ERROR)

        # Pending
        checkpoints = AggregatedKlineCheckpoint.objects.filter(
            symbol=symbol, last_time__gt=right_invalid_range_start_time
        )
        for checkpoint in checkpoints:
            self.assertEqual(checkpoint.is_1m_aggregated, CheckpointEnum.PENDING)

    def test_check_and_insert_5m(self):
        interval = "5m"
        qs = get_pending_checkpoint("is_5m_aggregated")
        arranged_checkpoints = arrange_checkpoint(interval, qs)
        symbol = "ETHUSDT"
        left_invalid_range_end_time = 1753326000000
        valid_range_start_time = 1753326000000
        valid_range_end_time = 1753326300000
        right_invalid_range_start_time = 1753326300000

        successful_insert = check_and_insert(interval, symbol, arranged_checkpoints[symbol])
        self.assertEqual(successful_insert, self.valid_5m_ranges)

        # Aggregated
        checkpoints = AggregatedKlineCheckpoint.objects.filter(
            symbol=symbol, first_time__gte=valid_range_start_time, last_time__lte=valid_range_end_time
        )
        for checkpoint in checkpoints:
            self.assertEqual(checkpoint.is_5m_aggregated, CheckpointEnum.AGGREGATED)

        # Error
        checkpoints = AggregatedKlineCheckpoint.objects.filter(
            symbol=symbol, first_time__lt=left_invalid_range_end_time
        )
        for checkpoint in checkpoints:
            self.assertEqual(checkpoint.is_5m_aggregated, CheckpointEnum.ERROR)

        # Pending
        checkpoints = AggregatedKlineCheckpoint.objects.filter(
            symbol=symbol, last_time__gt=right_invalid_range_start_time
        )
        for checkpoint in checkpoints:
            self.assertEqual(checkpoint.is_5m_aggregated, CheckpointEnum.PENDING)

    def test_check_and_insert_15m(self):
        interval = "15m"
        qs = get_pending_checkpoint("is_15m_aggregated")
        arranged_checkpoints = arrange_checkpoint(interval, qs)
        symbol = "ETHUSDT"
        left_invalid_range_end_time = 1753326000000
        valid_range_start_time = 1753326000000
        valid_range_end_time = 1753326300000
        right_invalid_range_start_time = 1753326300000

        successful_insert = check_and_insert(interval, symbol, arranged_checkpoints[symbol])
        self.assertEqual(successful_insert, 0)

        # Pending
        checkpoints = AggregatedKlineCheckpoint.objects.filter(symbol=symbol)
        for checkpoint in checkpoints:
            self.assertEqual(checkpoint.is_15m_aggregated, CheckpointEnum.PENDING)
