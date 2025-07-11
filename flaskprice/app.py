import threading
import time

import eventlet

from flaskprice.dispatcher import dispatch_data, consume_data

eventlet.monkey_patch()

from flask import Flask
from flask_socketio import SocketIO

from flaskprice.config import CORS_ORIGINS, SUPPORTED_STREAMS, SOCKETIO_HOST, SOCKETIO_PORT
from flaskprice.clients import ClientManager
from flaskprice.events import register_events

streams = SUPPORTED_STREAMS
ClientManager.initialize(streams)
client_manager = ClientManager.get_instance()

if __name__ == "__main__":
    print(client_manager.get_streams())
    time.sleep(2)
    app = Flask(__name__)
    socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins=CORS_ORIGINS)

    register_events(socketio)
    for stream in streams:
        socketio.start_background_task(dispatch_data, stream)

    t = threading.Thread(target=consume_data, daemon=True)  # ?consumer
    t.start()

    socketio.run(app, host=SOCKETIO_HOST, port=SOCKETIO_PORT)
