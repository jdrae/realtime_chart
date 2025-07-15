from flask import request
from flask_socketio import SocketIO

from flaskprice.config import SUPPORTED_STREAMS
from flaskprice.state import clients


def register_events(socketio: SocketIO):
    @socketio.on("connect")
    def handle_connect():
        sid = request.sid
        print(f"Client connected {sid}")

    @socketio.on("subscribe")
    def handle_subscribe(data):
        sid = request.sid
        stream = data.get("stream").upper()
        print(f"[{sid}][{stream}] subscribe")
        if stream in SUPPORTED_STREAMS:
            clients[stream].add(sid)
            print(clients)
        else:
            socketio.emit("error", {"message": f"invalid stream: {stream}"})
            print("error")
            return

    @socketio.on("disconnect")
    def handle_disconnect():
        sid = request.sid
        print(f"[{sid}] disconnect")
        for stream in SUPPORTED_STREAMS:
            clients[stream].discard(sid)
        print(clients)
