import asyncio
import json
import logging

from main.binance_connector.binance_enum import Symbol, StreamName
from main.common.kafka.async_kafka_publisher import AsyncKafkaPublisher
from main.common.utils import get_timestamp
from main.common.websocket.websocket_client import WebSocketClient


class DataHandler:
    def __init__(
        self,
        stream_name: StreamName,
        symbols: list[Symbol],
        publisher: AsyncKafkaPublisher,
        loop: asyncio.AbstractEventLoop,
    ):
        self.logger = logging.getLogger(__name__)
        self.id = get_timestamp()
        self.stream_names = list(map(lambda x: stream_name.value.format(x.value), symbols))
        self.stream_url = "wss://stream.binance.com:9443/stream"
        self.websocketClient = WebSocketClient(stream_url=self.stream_url, on_message=self.on_message)
        self.publisher = publisher
        self.loop = loop

    def __del__(self):
        self.logger.debug("DataHandler.__del__")
        self.stop()

    def on_message(self, data):
        if "id" in data:
            self.logger.debug(f"on_message: {data}")
        future = asyncio.run_coroutine_threadsafe(self.publisher.publish(data), self.loop)
        try:
            future.result(timeout=1)
        except Exception as e:
            self.logger.error("Kafka publish failed: {}".format(e), exc_info=True)

    def start(self):
        self.logger.info("Starting DataHandler")
        self.websocketClient.connect()  # start connection
        self.websocketClient.start()  # start thread
        self.subscribe()
        self.logger.info("DataHandler started")

    def stop(self):
        self.logger.info("Stopping DataHandler")
        if not self.websocketClient.ws.connected:
            self.logger.warning("DataHandler already closed")
            return
        self.unsubscribe()
        self.websocketClient.close()  # end connection
        self.websocketClient.join()  # end thread
        self.logger.info("DataHandler stopped")

    def subscribe(self):
        json_msg = json.dumps({"method": "SUBSCRIBE", "params": self.stream_names, "id": self.id})
        self.websocketClient.send(json_msg)
        self.logger.info("Subscribed: {}".format(self.stream_names))

    def unsubscribe(self):
        json_msg = json.dumps({"method": "UNSUBSCRIBE", "params": self.stream_names, "id": self.id})
        self.websocketClient.send(json_msg)
        self.logger.info("Unsubscribed: {}".format(self.stream_names))
