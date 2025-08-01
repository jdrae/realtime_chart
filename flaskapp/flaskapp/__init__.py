import os
import threading

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flaskapp.config import SUPPORTED_STREAMS
from flaskapp.dispatcher import dispatch_data
from flaskapp.events import register_events
from flaskapp.kafka_consumer import kafka_consumer_loop
from flaskapp.state import StreamManager

socketio = SocketIO(async_mode="threading", cors_allowed_origins=os.getenv("CORS_ORIGINS").split(","))
stream_manager = StreamManager(SUPPORTED_STREAMS)


def create_app():
    app = Flask(__name__)
    CORS(app, origins=os.getenv("CORS_ORIGINS").split(","))

    socketio.init_app(app)

    register_events(socketio, stream_manager)

    threading.Thread(target=kafka_consumer_loop, args=(stream_manager,), daemon=True).start()

    for stream in SUPPORTED_STREAMS:
        socketio.start_background_task(dispatch_data, socketio, stream_manager, stream)

    return app
