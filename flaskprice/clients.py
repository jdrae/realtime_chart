import threading
from queue import Queue


class ClientManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is not None:
            raise RuntimeError("Use get_instance() instead of direct instantiation.")
        return super().__new__(cls)

    def __init__(self, streams):
        self.streams = streams
        self.clients = {k: set() for k in streams}
        self.locks = {k: threading.Lock() for k in streams}
        self.queues = {k: Queue() for k in streams}

    @classmethod
    def initialize(cls, streams):
        with cls._lock:  # prevent initializing from other threads
            if cls._instance is None:
                cls._instance = cls(streams)  # call __init__
            else:
                raise RuntimeError("Singleton already initialized")

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            raise RuntimeError("Singleton not initialized. Call initialize() first.")
        return cls._instance

    def get_streams(self):
        return list(self.streams)  # return copy

    def get_client_list(self, stream):
        with self.locks[stream]:
            return set(self.clients[stream])  # return copy

    def add_client(self, stream, sid):
        self.clients[stream].add(sid)
        print("added:", self.clients)

    def remove_client(self, sid):
        for stream in self.streams:
            with self.locks[stream]:
                self.clients[stream].discard(sid)
        print("removed:", self.clients)
