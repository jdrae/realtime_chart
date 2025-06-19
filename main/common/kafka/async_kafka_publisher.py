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
        self.logger.info("Starting Kafka publisher")
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.brokers, value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        await self.producer.start()
        self.logger.info("Kafka publisher started")

    async def stop(self):
        self.logger.info("Stopping Kafka publisher")
        if self.producer:
            await self.producer.stop()
            self.logger.info("Kafka publisher stopped")

    async def publish(self, data: dict):
        if "id" in data:
            self.logger.debug(f"publish: {data}")
        await self.producer.send_and_wait(self.topic, data)
