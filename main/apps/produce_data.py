import asyncio
import logging
import os
import signal

from main.common.binance_connector.binance_enum import StreamName, Symbol
from main.common.binance_connector.data_handler import DataHandler
from main.common.kafka.async_kafka_publisher import AsyncKafkaPublisher
from main.common.utils import default_logger

logger = default_logger("main", logging.DEBUG)  # write project's root module to propagate log config


async def main():
    shutdown_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, lambda: shutdown_event.set())
    loop.add_signal_handler(signal.SIGTERM, lambda: shutdown_event.set())

    kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
    publisher = AsyncKafkaPublisher(
        brokers=kafka_bootstrap_servers, topic=os.getenv("KAFKA_TOPIC_MINITICKER")
    )
    await publisher.start()

    handler = DataHandler(
        stream_name=StreamName.MINI_TICKER, symbols=[Symbol.BTCUSDT], publisher=publisher, loop=loop
    )
    handler.start()

    try:
        await shutdown_event.wait()
    finally:
        handler.stop()
        await publisher.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.warning(f"Process finished unexpectedly: {e}")
