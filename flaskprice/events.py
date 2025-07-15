from flask import request
from flask_socketio import SocketIO

from flaskprice.state import StreamManager


def register_events(socketio: SocketIO, stream_manager: StreamManager):
    @socketio.on("connect")
    def handle_connect():
        sid = request.sid
        print(f"Client connected {sid}")

    @socketio.on("subscribe")
    def handle_subscribe(data):
        sid = request.sid
        stream = data.get("stream").upper()
        print(f"[{sid}][{stream}] subscribe")
        if stream in stream_manager.get_stream_names():
            stream_manager.add_client(stream, sid)
            print(stream_manager.get_clients(stream))
        else:
            socketio.emit("error", {"message": f"invalid stream: {stream}"})
            print("error")
            return

    @socketio.on("disconnect")
    def handle_disconnect():
        sid = request.sid
        print(f"[{sid}] disconnect")
        stream_manager.remove_client(request.sid)
