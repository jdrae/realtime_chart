from flask import request

from flaskprice.clients import ClientManager


def register_events(socketio):
    client_manager = ClientManager.get_instance()

    @socketio.on("connect")
    def handle_connect():
        sid = request.sid
        print(f"Client connected {sid}")

    @socketio.on("subscribe")
    def handle_subscribe(data):
        sid = request.sid
        stream = data.get("stream")
        print(f"[{sid}][{stream}] subscribe")
        if stream not in client_manager.get_streams():
            socketio.emit("error", {"message": f"invalid stream: {stream}"})
            return
        client_manager.add_client(sid, stream)

    @socketio.on("disconnect")
    def handle_disconnect():
        sid = request.sid
        print(f"[{sid}] disconnect")
        client_manager.remove_client(sid)
