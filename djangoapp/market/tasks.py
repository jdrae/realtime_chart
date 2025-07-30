import logging
import time

from celery import shared_task
from enums.interval import Interval
from market.serializers.aggregated_kline import AggregatedKLineSerializer
from market.services.kafka_publisher import publish_data_to_kafka
from market.services.kline_aggregator import (
    get_pending_checkpoint,
    arrange_checkpoint,
    check_and_insert,
)
from market.services.time_utils import ms_to_utctime

logger = logging.getLogger(__name__)


@shared_task
def aggregate_1m():
    logger.info("Starting task aggregate_1m")
    interval = "1m"
    kafka_topic = "aggregated_kline_1m"
    target_column = Interval.from_label(interval).column
    retries = 3
    wait_sec = 4

    while retries:
        time.sleep(wait_sec)
        retries -= 1
        checkpoints = get_pending_checkpoint(target_column)
        if len(checkpoints) == 0:  # until all checkpoints are handled
            logger.info("All checkpoints handled in aggregate_1m")
            break
        arranged_checkpoints = arrange_checkpoint(interval, checkpoints)
        for symbol, ranges in arranged_checkpoints.items():
            inserted_data = check_and_insert(interval, symbol, ranges)
            serialized_data = AggregatedKLineSerializer(inserted_data, many=True)
            # TODO: publish inserted data to calculate indicators
