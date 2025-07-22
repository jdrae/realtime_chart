import argparse
import configparser
import logging
import os
import signal
import sys

from main.common.checkpoint_handler import KlineCheckpointHandler
from main.common.entity import *
from main.common.entity_mapper import get_json_entity_mapper
from main.common.kafka_consumer import KafkaConsumerManager
from main.common.postgres_client import BatchInserter, PostgresClient
from main.common.postgres_kafka_data_handler import PostgresKafkaDataHandler
from main.common.utils import default_logger

logger = default_logger("main", logging.DEBUG)


def handle_exit(signum, frame):
    signal_name = signal.Signals(signum).name
    logger.warning(f"Received signal {signal_name}, exiting process.")
    sys.exit(0)


signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)


def save_data(stream):
    config = configparser.ConfigParser()
    config.read("config.ini")

    try:
        stream = stream.upper()
        logger.info(f"Start app with stream: {stream}")
        for cfg in config[stream].keys():
            logger.info("[{}] {}".format(cfg, config[stream][cfg]))
    except:
        logger.warning(f"Configuration error: --stream {stream}")

    db_client = PostgresClient()

    mapper = get_json_entity_mapper(stream)
    target_class = mapper.get_target_class()

    checkpoint_handler = KlineCheckpointHandler(db_client, table=config[stream]["POSTGRES_TABLE_CHECKPOINT"])

    inserter_processed = BatchInserter(
        db_client,
        query=target_class.sql_insert(config[stream]["POSTGRES_TABLE_PROCESSED"]),
        batch_size=60,
        checkpoint_handler=checkpoint_handler,
    )
    inserter_raw = BatchInserter(
        db_client, query=Raw.sql_insert(config[stream]["POSTGRES_TABLE_RAW"]), batch_size=60
    )
    inserter_failed = BatchInserter(
        db_client,
        query=Failed.sql_insert(config[stream]["POSTGRES_TABLE_FAILED"]),
        batch_size=1,
    )

    handler = PostgresKafkaDataHandler(
        group_id=config[stream]["KAFKA_GROUP_POSTGRES"],
        mapper=mapper,
        inserter_processed=inserter_processed,
        inserter_raw=inserter_raw,
        inserter_failed=inserter_failed,
    )

    consumer = KafkaConsumerManager(
        brokers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
        topic=config[stream]["KAFKA_TOPIC"],
        handler=handler,
    )

    try:
        db_client.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
        )
        inserter_processed.start()
        inserter_raw.start()
        inserter_failed.start()
        consumer.run()
    finally:
        inserter_processed.stop()
        inserter_raw.stop()
        inserter_failed.stop()
        db_client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stream", type=str, required=True)
    args = parser.parse_args()

    try:
        save_data(stream=args.stream)
    except Exception as e:
        logger.critical(f"Process finished unexpectedly: {e}")
