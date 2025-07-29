import json
import logging
from abc import ABC, abstractmethod

from kafka import KafkaConsumer


class KafkaDataHandler(ABC):
    def __init__(self, group_id):
        self.logger = logging.getLogger(__name__)
        self.group_id = group_id

    @abstractmethod
    def handle(self, data: str):
        pass


class KafkaConsumerManager:
    def __init__(self, brokers: str, topic: str, handler: KafkaDataHandler):
        self.logger = logging.getLogger(__name__)
        self.topic = topic
        self.handler = handler
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=brokers,
            value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            group_id=self.handler.group_id,
        )

    def run(self):
        self.logger.info(f"Listening to topic: {self.topic}")
        for message in self.consumer:
            data = message.value  # str
            try:
                self.handler.handle(data)
            except Exception as e:
                self.logger.error(f"Error handling message: {e}", exc_info=True)
