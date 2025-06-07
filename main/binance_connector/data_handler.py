import json
import logging

from main.common.utils import get_timestamp, default_logger
from main.common.websocket.websocket_client import WebSocketClient


class DataHandler:
    ACTION_SUBSCRIBE = "SUBSCRIBE"
    ACTION_UNSUBSCRIBE = "UNSUBSCRIBE"

    def __init__(self, symbol: str):
        self.logger = logging.getLogger(__name__)
        self.symbol = symbol.lower()
        self.stream_url = "wss://stream.binance.com:9443/stream"
        self.websocketClient = WebSocketClient(stream_url=self.stream_url, on_message=self.on_message)

    def on_message(self, data):
        print(data)

    def subscribe(self, stream_name: str, id=None):
        if not id:
            id = get_timestamp()
        json_msg = json.dumps({"method": "SUBSCRIBE", "params": [stream_name], "id": id})
        self.websocketClient.send(json_msg)
        self.logger.info("Stream name {} subscribed".format(stream_name))

    def unsubscribe(self, stream_name: str, id=None):
        if not id:
            id = get_timestamp()
        json_msg = json.dumps({"method": "UNSUBSCRIBE", "params": [stream_name], "id": id})
        self.websocketClient.send(json_msg)
        self.logger.info("Stream name {} unsubscribed".format(stream_name))

    ### Wrapped Methods ###
    def start(self):
        self.logger.info("Starting data handler")
        self.websocketClient.connect() # start connection
        self.websocketClient.start() # start thread
        self.logger.info("Data handler started")

    def stop(self):
        self.logger.info("Stopping data handler")
        self.websocketClient.close() # end connection
        self.websocketClient.join() # end thread
        self.logger.info("Data handler stopped")

    ### Used Streams ###
    def mini_ticker(self, id=None, action=None):
        stream_name = "{}@miniTicker".format(self.symbol)

        if action is None:
            self.subscribe(stream_name, id)
        elif action == "unsubscribe":
            self.unsubscribe(stream_name, id)

    def kline(self, interval: str, id=None, action=None):
        stream_name = "{}@kline_{}".format(self.symbol, interval)

        if action is None:
            self.subscribe(stream_name, id)
        elif action == DataHandler.ACTION_UNSUBSCRIBE:
            self.unsubscribe(stream_name, id)
