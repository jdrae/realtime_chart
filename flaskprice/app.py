import logging

import eventlet

eventlet.monkey_patch()

from flaskprice.dispatcher import dispatch_data
from flaskprice.kafka_consumer import kafka_consumer_loop
from flaskprice.logger import default_logger
from flaskprice.state import StreamManager

from flask import Flask
from flask_socketio import SocketIO
import threading

from flaskprice.config import CORS_ORIGINS, SUPPORTED_STREAMS, SOCKETIO_HOST, SOCKETIO_PORT
from flaskprice.events import register_events

logger = default_logger("flaskprice", logging.DEBUG)

app = Flask(__name__)
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins=CORS_ORIGINS)
stream_manager = StreamManager(SUPPORTED_STREAMS)


def main():

    register_events(socketio, stream_manager)

    threading.Thread(target=kafka_consumer_loop, args=(stream_manager,), daemon=True).start()

    for stream in SUPPORTED_STREAMS:
        socketio.start_background_task(dispatch_data, socketio, stream_manager, stream)

    socketio.run(app, host=SOCKETIO_HOST, port=SOCKETIO_PORT)


if __name__ == "__main__":
    logger.info(f"Starting app in {SOCKETIO_HOST}:{SOCKETIO_PORT}")
    main()
