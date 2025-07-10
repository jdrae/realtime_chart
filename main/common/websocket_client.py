import logging
import threading
import time

import websocket


class WebsocketClient(threading.Thread):
    def __init__(self, stream_url, on_message):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.stream_url = stream_url
        self.ws = None
        self.on_message = on_message

    def start(self):
        self.connect()  # start connection
        super().start()  # start thread

    def stop(self):
        self.close()  # end connection
        super().join()  # end threa

    def ping(self):
        self.logger.debug("Sending ping to Binance WebSocket Server")
        self.ws.ping()

    def send(self, message):
        self.logger.debug("Sending message to WebSocket Server: {}".format(message))
        self.ws.send(message)

    def connect(self):
        self.logger.debug("Connecting to websocket")
        self.ws = websocket.create_connection(self.stream_url)
        self.logger.debug("Connected to websocket")

    def close(self):
        self.logger.debug("Closing websocket")
        if not self.ws.connected:
            self.logger.warning("Websocket already closed")
        else:
            self.ws.send_close()
            self.logger.debug("Websocket closed")

    def run(self):
        self.read_data()

    def read_data(self):
        while True:
            try:
                op_code, frame = self.ws.recv_data_frame(True)
            except Exception as e:
                self._handle_websocket_exception(e)
                break
            if op_code == websocket.ABNF.OPCODE_CLOSE:
                self.logger.warning("CLOSE frame received, closing websocket connection")
                break
            elif op_code == websocket.ABNF.OPCODE_TEXT:
                self._handle_data(op_code, frame)
            else:
                self._handle_heartbeat(op_code, frame)

    def _handle_data(self, op_code, frame):
        received_at = int(time.time() * 1000)
        data = frame.data.decode("utf-8")
        data = data[:-1] + ', "received_at": ' + str(received_at) + "}"
        self._callback(self.on_message, data)

    def _handle_heartbeat(self, op_code, frame):
        if op_code == websocket.ABNF.OPCODE_PING:
            self.ws.pong("")
            self.logger.debug("Received Ping; PONG frame sent back")
        elif op_code == websocket.ABNF.OPCODE_PONG:
            self.logger.debug("Received PONG frame")
        else:
            self.logger.warning("unknown opcode received: {} (frame: {})".format(op_code, frame))

    def _handle_websocket_exception(self, e):
        if isinstance(e, websocket.WebSocketConnectionClosedException):
            self.logger.error("Lost websocket connection: {}".format(e), exc_info=True)
        elif isinstance(e, websocket.WebSocketTimeoutException):
            self.logger.error("Websocket connection timeout: {}".format(e), exc_info=True)
        elif isinstance(e, websocket.WebSocketException):
            self.logger.error("Websocket exception: {}".format(e), exc_info=True)
        else:
            self.logger.error("Exception in read_data: {}".format(e), exc_info=True)
            self._handle_exception(e)

    def _callback(self, callback, *args):
        if callback:
            try:
                callback(*args)
            except Exception as e:
                self.logger.error("Error from callback {}: {}".format(callback, e), exc_info=True)
                self._handle_exception(e)

    def _handle_exception(self, e):
        raise e
