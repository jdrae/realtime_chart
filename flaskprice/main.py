import json
import time
from queue import Queue
from threading import Thread

import eventlet

eventlet.monkey_patch()

from flask import Flask, request, render_template
from flask_socketio import SocketIO, emit
from kafka import KafkaConsumer


app = Flask(__name__)
socketio = SocketIO(app, async_mode="eventlet")

TOPICS = ["btc", "eth", "xrp"]


@app.route("/<symbol>")
def index(symbol):
    if symbol not in TOPICS:
        return "Invalid symbol", 404
    return render_template("index.html", topic=symbol)


clients = {k: set() for k in TOPICS}
send_queue = Queue()


def start_dispatchers():
    for topic in TOPICS:
        thread = Thread(target=lambda: consume_data(topic), daemon=True)
        thread.start()
        print("Started dispatcher for topic {}".format(topic))


def consume_data(topic):
    consumer = KafkaConsumer(
        "miniticker",
        bootstrap_servers="localhost:9092",
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id=f"{topic}-group",
    )
    print("Started kafka consumer for topic {}".format(topic))

    for msg in consumer:
        data = json.loads(msg.value)  # str -> dict
        print("." + topic[0])
        for sid in clients[topic]:
            send_queue.put({"sid": sid, "topic": topic, "data": data})


def dispatch_data():
    print("Started sender")
    while True:
        info = send_queue.get(block=True, timeout=None)
        sid, topic, data = info["sid"], info["topic"], info["data"]
        if sid in clients[topic]:  # skip if client is disconnected or unsubscribed
            print("sending...")
            time.sleep(3)
            socketio.emit("message", data)
            print("sent!")


@socketio.on("connect")
def handle_connect():
    sid = request.sid
    print(f"Client connected {sid}")


@socketio.on("subscribe")
def handle_subscribe(data):
    sid = request.sid
    topic = data["topic"]
    print(f"[{sid}][{topic}] subscribe")
    if topic not in TOPICS:
        emit("error", {"message": "invalid topic"})
        return

    clients[topic].add(sid)


@socketio.on("disconnect")
def handle_disconnect():
    # when web page is loaded, it automatically disconnects previous websocket connection
    sid = request.sid
    print(f"[{sid}] disconnect")

    for lst in clients.values():
        lst.discard(sid)


if __name__ == "__main__":
    start_dispatchers()
    socketio.start_background_task(dispatch_data)
    socketio.run(app, host="localhost", port=5555)
