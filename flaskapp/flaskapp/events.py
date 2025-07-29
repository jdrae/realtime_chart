import logging

from flask import request
from flask_socketio import SocketIO, join_room, leave_room
from flaskapp.state import StreamManager


def register_events(socketio: SocketIO, stream_manager: StreamManager):
    logger = logging.getLogger(__name__)

    @socketio.on("connect")
    def handle_connect():
        sid = request.sid
        logger.debug(f"[{sid}] connected")

    @socketio.on("subscribe")
    def handle_subscribe(data):
        sid = request.sid
        stream = data.get("stream").upper()
        if stream in stream_manager.get_stream_names():
            join_room(room=stream)
        else:
            socketio.emit("error", {"message": f"invalid stream: {stream}"})
            logger.error(f"Invalid stream from client: {stream}")
            return
        logger.debug(f"[{sid}][{stream}] subscribed")

    @socketio.on("disconnect")
    def handle_disconnect():
        sid = request.sid
        for stream in stream_manager.get_stream_names():
            leave_room(room=stream, sid=sid)
        logger.debug(f"[{sid}] disconnected")
