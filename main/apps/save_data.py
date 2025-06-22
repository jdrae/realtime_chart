import configparser
import logging
import os

from main.common.entity import *
from main.common.entity_mapper import MiniTickerEntityMapper
from main.common.kafka_consumer import KafkaConsumerManager
from main.common.postgres_client import BatchInserter, PostgresClient
from main.common.postgres_kafka_data_handler import PostgresKafkaDataHandler
from main.common.utils import default_logger

logger = default_logger("main", logging.DEBUG)


def save_data(target_stream):
    config = configparser.ConfigParser()
    config.read("config.ini")

    logger.info("Start app with stream: {}".format(target_stream))
    for cfg in config[target_stream].keys():
        logger.info("[{}] {}".format(cfg, config[target_stream][cfg]))

    db_client = PostgresClient()

    inserter_processed = BatchInserter(
        db_client,
        MiniTicker.sql_insert(config[target_stream]["POSTGRES_TABLE_PROCESSED"], bulk=True),
        batch_size=40,
    )
    inserter_raw = BatchInserter(
        db_client, Raw.sql_insert(config[target_stream]["POSTGRES_TABLE_RAW"], bulk=True), batch_size=40
    )
    inserter_failed = BatchInserter(
        db_client,
        Failed.sql_insert(config[target_stream]["POSTGRES_TABLE_FAILED"], bulk=True),
        batch_size=1,
    )

    handler = PostgresKafkaDataHandler(
        config[target_stream]["KAFKA_GROUP_POSTGRES"],
        MiniTickerEntityMapper(),
        inserter_processed=inserter_processed,
        inserter_raw=inserter_raw,
        inserter_failed=inserter_failed,
    )

    consumer = KafkaConsumerManager(
        brokers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
        topic=config[target_stream]["KAFKA_TOPIC"],
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
    target_stream = "MINITICKER"

    save_data(target_stream)
