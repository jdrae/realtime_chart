import configparser
import logging
import os

from pythonprice.common.indicator import MovingAverageCalculator
from pythonprice.common.indicator_kafka_data_handler import IndicatorKafkaDataHandler
from pythonprice.common.kafka_consumer import KafkaConsumerManager
from pythonprice.common.postgres_client import PostgresClient
from pythonprice.common.utils import default_logger

logger = default_logger("pythonprice", logging.DEBUG)


config = configparser.ConfigParser()
config.read("config.ini")

symbols = config["SYMBOLS"]

db_client = PostgresClient()

handler = IndicatorKafkaDataHandler(
    group_id="ma7",
    db_client=db_client,
    indicators={
        symbol: [MovingAverageCalculator("1m", 7), MovingAverageCalculator("1m", 20)] for symbol in symbols
    },
    fail_table="indicator_failed",
    processed_table="indicator",
)

consumer = KafkaConsumerManager(
    brokers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
    topic=config["INDICATOR"]["KAFKA_TOPIC"],
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
    consumer.run()
finally:
    db_client.close()
