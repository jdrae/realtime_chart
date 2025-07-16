import json

from kafka import KafkaConsumer

from flaskprice.config import KAFKA_TOPIC, KAFKA_BOOTSTRAP_SERVERS, KAFKA_GROUP_ID
from flaskprice.state import StreamManager


def kafka_consumer_loop(stream_manager: StreamManager):
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        group_id=KAFKA_GROUP_ID,
    )

    print(f"Listening to topic: {KAFKA_TOPIC}, group: {KAFKA_GROUP_ID}")
    for message in consumer:
        data = message.value  # str
        try:
            data = json.loads(data)
            if "data" not in data:
                print("Received unexpected data:", data)
                continue

            stream = data["data"]["s"]
            if stream not in stream_manager.get_stream_names():
                raise ValueError("Invalid stream:", stream)

            stream_manager.put_payload(stream, {"stream": stream, "data": data})
        except Exception as e:
            print(f"Error handling message: {e}")
