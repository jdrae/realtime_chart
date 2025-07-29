import argparse
import asyncio
import configparser
import logging
import os
import signal

from pythonapp.common.binance_connector import BinanceConnector
from pythonapp.common.kafka_publisher_async import AsyncKafkaPublisher
from pythonapp.common.utils import default_logger
from pythonapp.common.websocket_client import WebsocketClient

logger = default_logger("pythonapp", logging.DEBUG)  # write project's root module to propagate log config


def handle_exit(signum, shutdown_event):
    signal_name = signal.Signals(signum).name
    logger.warning(f"Received signal {signal_name}, exiting process.")
    shutdown_event.set()


async def produce_data(stream, symbols):
    config = configparser.ConfigParser()
    config.read("pythonapp/config.ini")  # TODO: change to config.py

    try:
        stream = stream.upper()
        symbols = list(map(lambda x: config["SYMBOL"][x], symbols))
        logger.info(f"Start app with stream: {stream}, symbols: {symbols}")
        for cfg in config[stream].keys():
            logger.info("[{}] {}".format(cfg, config[stream][cfg]))
    except:
        logger.warning(f"Configuration error: --stream {stream} --symbols {symbols}")

    loop = asyncio.get_running_loop()
    shutdown_event = asyncio.Event()
    loop.add_signal_handler(signal.SIGINT, lambda: handle_exit(signal.SIGINT, shutdown_event))
    loop.add_signal_handler(signal.SIGTERM, lambda: handle_exit(signal.SIGTERM, shutdown_event))

    publisher = AsyncKafkaPublisher(
        brokers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"), topic=config[stream]["KAFKA_TOPIC"]
    )
    # TODO: handle future timeout exception
    websocket = WebsocketClient(
        stream_url=config["WEBSOCKET_URL"]["STREAM"],
        on_message=lambda data: asyncio.run_coroutine_threadsafe(publisher.publish(data), loop),
    )

    connector = BinanceConnector(
        stream_name=config[stream]["STREAM_NAME"],
        symbols=symbols,
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--stream", type=str, required=True)
    parser.add_argument("--symbols", nargs="+", type=str, required=True)
    args = parser.parse_args()

    try:
        asyncio.run(produce_data(stream=args.stream, symbols=args.symbols))
    except Exception as e:
        logger.critical(f"Process finished unexpectedly: {e}")
