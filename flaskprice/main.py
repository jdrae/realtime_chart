import json

import eventlet

eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO
from kafka import KafkaConsumer


app = Flask(__name__)
socketio = SocketIO(app)

KAFKA_BROKER = "localhost:9092"
TOPIC_NAME = "miniticker"


@app.route("/")
def index():
    return render_template("index.html")


def consume_kafka():
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="flask-miniticker",
    )

    for message in consumer:
        data = json.loads(message.value)
        print(f"Received from Kafka: {type(data)} {data}")
        socketio.emit("random_number", data)


@socketio.on("connect")
def handle_connect():
    print("Client connected")
    socketio.start_background_task(target=consume_kafka)


if __name__ == "__main__":
    socketio.run(app, debug=True)
