import queue
from threading import Lock
from typing import Dict, Set


class ThreadSafeSet:
    def __init__(self):
        self._set = set()
        self._lock = Lock()

    def add(self, value):
        with self._lock:
            self._set.add(value)

    def discard(self, value):
        with self._lock:
            self._set.discard(value)

    def copy(self) -> set:
        with self._lock:
            return self._set.copy()


class Stream:
    def __init__(self):
        self.clients = ThreadSafeSet()
        self.queue = queue.Queue()


class StreamManager:
    def __init__(self, streams: Set[str]):
        self._streams: Dict[str, Stream] = {stream: Stream() for stream in streams}

    def get_stream_names(self) -> Set[str]:
        return set(self._streams.keys())

    # handle set
    def get_clients(self, stream: str) -> set:
        return self._streams[stream].clients.copy()

    def add_client(self, stream: str, sid: str):
        self._streams[stream].clients.add(sid)

    def remove_client(self, sid: str):
        for stream in self.get_stream_names():
            self._streams[stream].clients.discard(sid)

    # handle queue
    def get_queue(self, stream: str) -> queue.Queue:
        return self._streams[stream].queue

    def put_payload(self, stream: str, payload: dict):
        self._streams[stream].queue.put(payload)
