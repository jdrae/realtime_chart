import logging
import os

from main.common.kafka_consumer import KafkaConsumerManager, PostgresDataConsumer
from main.common.postgres_client import PostgresClient
from main.common.utils import default_logger

logger = default_logger("main", logging.DEBUG)


if __name__ == "__main__":
    db_client = PostgresClient(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
    )
    handler = PostgresDataConsumer(db_client, table="miniticker_raw", group_id="miniticker_dev")
    consumer = KafkaConsumerManager(
        brokers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
        topic=os.getenv("KAFKA_TOPIC_MINITICKER"),
        handler=handler,
    )

    try:
        consumer.run()
    finally:
        db_client.close()
