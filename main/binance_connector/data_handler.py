import json
import logging

from main.binance_connector.binance_enum import Symbol, StreamName
from main.common.utils import get_timestamp
from main.common.websocket.websocket_client import WebSocketClient


class DataHandler:
    def __init__(self, stream_name: StreamName, symbols: list[Symbol]):
        self.logger = logging.getLogger(__name__)
        self.id = get_timestamp()
        self.stream_names = list(map(lambda x: stream_name.value.format(x.value), symbols))
        self.stream_url = "wss://stream.binance.com:9443/stream"
        self.websocketClient = WebSocketClient(stream_url=self.stream_url, on_message=self.on_message)

    def on_message(self, data):
        print(data)

    def start(self):
        self.logger.info("Starting data handler")
        self.websocketClient.connect() # start connection
        self.websocketClient.start() # start thread
        self.subscribe()
        self.logger.info("Data handler started")

    def stop(self):
        self.logger.info("Stopping data handler")
        self.unsubscribe()
        self.websocketClient.close() # end connection
        self.websocketClient.join() # end thread
        self.logger.info("Data handler stopped")

    def subscribe(self):
        json_msg = json.dumps({"method": "SUBSCRIBE", "params": self.stream_names, "id": self.id})
        self.websocketClient.send(json_msg)
        self.logger.info("Subscribed: {}".format(self.stream_names))

    def unsubscribe(self):
        json_msg = json.dumps({"method": "UNSUBSCRIBE", "params": self.stream_names, "id": self.id})
        self.websocketClient.send(json_msg)
        self.logger.info("Unsubscribed: {}".format(self.stream_names))
