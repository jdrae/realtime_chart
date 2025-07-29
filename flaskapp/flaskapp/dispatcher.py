import logging

from flask_socketio import SocketIO
from flaskapp.state import StreamManager


def dispatch_data(socketio: SocketIO, stream_manager: StreamManager, stream: str):
    logger = logging.getLogger(__name__)

    queue = stream_manager.get_queue(stream)
    logger.info(f"Dispatcher started: {stream}")
    while True:
        try:
            payload = queue.get(block=True)  # blocking
            stream, data = payload["stream"], payload["data"]
            socketio.emit("message", data, to=stream)
        except Exception as e:
            logger.error(f"Dispatch error in {stream}: {e}", exc_info=e)
