import json

from kafka import KafkaConsumer

from flaskprice.clients import ClientManager
from flaskprice.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_GROUP_ID, KAFKA_TOPIC, SYMBOL_TO_STREAM


def consume_data():
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
    client_manager = ClientManager.get_instance()

    data = json.loads(data)
    if "data" not in data:
        print("Received unexpected data:", data)
        return
    stream = SYMBOL_TO_STREAM[data["data"]["s"]]
    for sid in client_manager.get_client_list(stream):
        client_manager.queues[stream].put({"sid": sid, "stream": stream, "data": data})


def dispatch_data(stream: str):
    client_manager = ClientManager.get_instance()
    queue = client_manager.queues[stream]
    print(f"Started dispatcher: {stream}")
    while True:
        info = queue.get(block=True, timeout=None)
        sid, stream, data = info["sid"], info["stream"], info["data"]
        if sid in client_manager.get_client_list(stream):  # check client is connected and subscribed
            socketio.emit("message", data)
        # task done?
