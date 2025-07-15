import eventlet
from flask_socketio import SocketIO

from flaskprice.state import StreamManager


def dispatch_data(socketio: SocketIO, stream_manager: StreamManager, stream: str):
    queue = stream_manager.get_queue(stream)
    print(f"Started dispatcher: {stream}")
    while True:
        if not queue.empty():
            info = queue.get()
            sid, stream, data = info["sid"], info["stream"], info["data"]
            if sid in stream_manager.get_clients(stream):  # check client is connected and subscribed
                socketio.emit("message", data, to=sid)
        eventlet.sleep(0.1)
