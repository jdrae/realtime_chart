import asyncio
import logging
import os

from main.binance_connector.binance_enum import StreamName, Symbol
from main.binance_connector.data_handler import DataHandler
from main.common.kafka.async_kafka_publisher import AsyncKafkaPublisher
from main.common.utils import default_logger

logger = default_logger("main", logging.DEBUG)  # write project's root module to propagate log config

async def main():
    loop = asyncio.get_running_loop()

    kafka_bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
    publisher = AsyncKafkaPublisher(brokers=kafka_bootstrap_servers, topic="dev-topic")
    await publisher.start()

    handler = DataHandler(stream_name=StreamName.MINI_TICKER,
                          symbols=[Symbol.BTCUSDT],
                          publisher=publisher,
                          loop=loop)
    handler.start()

    await asyncio.sleep(5)

    handler.stop()
    await publisher.stop()

if __name__ == "__main__":
    asyncio.run(main())