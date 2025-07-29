import json

from config.settings import KAFKA_BOOTSTRAP_SERVERS
from kafka import KafkaProducer


def get_producer():
    if not hasattr(get_producer, "producer"):
        get_producer.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
    return get_producer.producer


def publish_data_to_kafka(topic, data):
    try:
        get_producer().send(topic=topic, value=data)
        get_producer().flush()
    except Exception as e:
        print(e)
