import asyncio
import configparser
import logging
import os
import signal

from main.common.binance_connector import BinanceConnector
from main.common.kafka_publisher_async import AsyncKafkaPublisher
from main.common.utils import default_logger
from main.common.websocket_client import WebsocketClient

logger = default_logger("main", logging.DEBUG)  # write project's root module to propagate log config


async def produce_data(target_stream, target_symbols):
    config = configparser.ConfigParser()
    config.read("config.ini")

    shutdown_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, lambda: shutdown_event.set())
    loop.add_signal_handler(signal.SIGTERM, lambda: shutdown_event.set())

    publisher = AsyncKafkaPublisher(
        brokers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"), topic=config[target_stream]["KAFKA_TOPIC"]
    )
    # TODO: handle future timeout exception
    websocket = WebsocketClient(
        stream_url=config["WEBSOCKET_URL"]["STREAM"],
        on_message=lambda data: asyncio.run_coroutine_threadsafe(publisher.publish(data), loop),
    )
    connector = BinanceConnector(
        stream_name=config[target_stream]["STREAM_NAME"],
        symbols=list(map(lambda x: config["SYMBOL"][x], target_symbols)),
        websocket=websocket,
    )

    await publisher.start()
    websocket.start()
    websocket.ping()  # TODO: send 1 ping per 3 min
    connector.subscribe()

    try:
        await shutdown_event.wait()
    finally:
        connector.unsubscribe()
        websocket.stop()
        await publisher.stop()


if __name__ == "__main__":
    target_stream = "MINITICKER"
    target_symbols = ["btcusdt"]

    try:
        asyncio.run(produce_data(target_stream, target_symbols))
    except Exception as e:
        logger.warning(f"Process finished unexpectedly: {e}")
