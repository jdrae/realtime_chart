import eventlet
from flask_socketio import SocketIO

from flaskprice.state import queues, clients


def dispatch_data(socketio: SocketIO, stream: str):
    queue = queues[stream]
    print(f"Started dispatcher: {stream}")
    while True:
        if not queue.empty():
            info = queue.get()
            sid, stream, data = info["sid"], info["stream"], info["data"]
            if sid in clients[stream]:  # check client is connected and subscribed
                socketio.emit("message", data)
        eventlet.sleep(0.1)
