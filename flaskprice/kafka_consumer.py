import json

from kafka import KafkaConsumer

from flaskprice.config import KAFKA_TOPIC, KAFKA_BOOTSTRAP_SERVERS, KAFKA_GROUP_ID
from flaskprice.state import queues, clients


def kafka_consumer_loop():

    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        group_id=KAFKA_GROUP_ID,
        auto_offset_reset="latest",
    )

    print(f"Listening to topic: {KAFKA_TOPIC}, group: {KAFKA_GROUP_ID}")
    for message in consumer:
        data = message.value  # str
        try:
            assign_data(data)
        except Exception as e:
            print(f"Error handling message: {e}")


def assign_data(data: str):
    data = json.loads(data)
    if "data" not in data:
        print("Received unexpected data:", data)
        return
    stream = data["data"]["s"]
    if stream not in clients:
        raise ValueError("Invalid stream:", stream)
    for sid in clients[stream]:
        queues[stream].put({"sid": sid, "stream": stream, "data": data})
