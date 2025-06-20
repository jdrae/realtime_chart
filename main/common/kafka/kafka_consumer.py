import json
import logging
from abc import ABC, abstractmethod

from kafka import KafkaConsumer


class DataConsumer(ABC):
    def __init__(self, group_id):
        self.logger = logging.getLogger(__name__)
        self.group_id = group_id

    @abstractmethod
    def handle(self, data: dict):
        pass


class PostgresDataConsumer(DataConsumer):
    def __init__(self, db_client, table, group_id):
        super().__init__(group_id)
        self.logger.info(f"PostgresDataConsumer prepared with table: {table}, group_id: {group_id}")
        self.db_client = db_client
        self.table = table

    def handle(self, data: dict):
        self.db_client.insert_raw_data(self.table, data)
        self.logger.debug(f"Data inserted:{data}")


class KafkaConsumerManager:
    def __init__(self, brokers: str, topic: str, handler: DataConsumer):
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
            data = message.value
            try:
                self.logger.debug(f"received:{data} type:{type(data)}")
                self.handler.handle(data)
            except Exception as e:
                self.logger.error(f"Error handling message: {e}", exc_info=True)
