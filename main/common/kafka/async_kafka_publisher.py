import json
import logging

from aiokafka import AIOKafkaProducer


class AsyncKafkaPublisher:
    def __init__(self, brokers: str, topic: str):
        self.logger = logging.getLogger(__name__)
        self.brokers = brokers
        self.topic = topic
        self.producer = None

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.brokers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        await self.producer.start()

    async def stop(self):
        if self.producer:
            await self.producer.stop()

    async def publish(self, data: dict):
        self.logger.debug(data)
        await self.producer.send_and_wait(self.topic, data)
