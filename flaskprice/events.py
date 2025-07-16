from flask import request
from flask_socketio import SocketIO, join_room, leave_room

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
        if stream in stream_manager.get_stream_names():
            join_room(room=stream)
        else:
            socketio.emit("error", {"message": f"invalid stream: {stream}"})
            print("error")
            return
        print(f"[{sid}][{stream}] subscribed")

    @socketio.on("disconnect")
    def handle_disconnect():
        sid = request.sid
        for stream in stream_manager.get_stream_names():
            leave_room(room=stream, sid=sid)
        print(f"[{sid}] disconnected")
