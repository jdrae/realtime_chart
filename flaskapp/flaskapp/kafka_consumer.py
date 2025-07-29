import json
import logging
import os

from flaskapp.config import KAFKA_TOPIC, KAFKA_GROUP_ID
from flaskapp.state import StreamManager
from kafka import KafkaConsumer


def kafka_consumer_loop(stream_manager: StreamManager):
    logger = logging.getLogger(__name__)
    logger.info(f"Connecting to kafka: {os.getenv('KAFKA_BOOTSTRAP_SERVERS')}")

    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        group_id=KAFKA_GROUP_ID,
    )

    logger.info(f"Listening to topic: {KAFKA_TOPIC}, group: {KAFKA_GROUP_ID}")
    for message in consumer:
        data = message.value  # str
        try:
            data = json.loads(data)
            if "data" not in data:
                logger.warning(f"Received unexpected data from server: {data}")
                continue

            stream = data["data"]["s"]
            if stream not in stream_manager.get_stream_names():
                raise ValueError(f"Received unexpected stream from server: {data}")

            stream_manager.put_payload(stream, {"stream": stream, "data": data})
        except Exception as e:
            logger.error(f"Consumer error: {e}", exc_info=True)
