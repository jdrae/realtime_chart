from flask_socketio import SocketIO

from flaskprice.state import StreamManager


def dispatch_data(socketio: SocketIO, stream_manager: StreamManager, stream: str):
    queue = stream_manager.get_queue(stream)
    print(f"Started dispatcher: {stream}")
    while True:
        try:
            payload = queue.get(block=True)  # blocking
            stream, data = payload["stream"], payload["data"]
            socketio.emit("message", data, to=stream)
        except Exception as e:
            print(f"Dispatch error in {stream}: {e}")
