import json
import logging

from pythonprice.common.utils import get_timestamp
from pythonprice.common.websocket_client import WebsocketClient


class BinanceConnector:
    def __init__(self, stream_name, symbols, websocket: WebsocketClient):
        self.logger = logging.getLogger(__name__)
        self.id = get_timestamp()
        self.stream_names = list(map(lambda x: stream_name.format(x), symbols))
        self.websocket = websocket

    def subscribe(self):
        json_msg = json.dumps({"method": "SUBSCRIBE", "params": self.stream_names, "id": self.id})
        self.websocket.send(json_msg)
        self.logger.info("Subscribed: {}".format(self.stream_names))

    def unsubscribe(self):
        json_msg = json.dumps({"method": "UNSUBSCRIBE", "params": self.stream_names, "id": self.id})
        self.websocket.send(json_msg)
        self.logger.info("Unsubscribed: {}".format(self.stream_names))
