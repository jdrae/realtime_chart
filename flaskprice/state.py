from queue import Queue
from typing import Set


class StreamManager:
    def __init__(self, streams: Set[str]):
        self._streams = streams
        self._queues = {stream: Queue() for stream in streams}

    def get_stream_names(self) -> Set[str]:
        return self._streams

    def get_queue(self, stream: str) -> Queue:
        return self._queues[stream]

    def put_payload(self, stream: str, payload: dict):
        self._queues[stream].put(payload)
