import queue
from typing import Dict, Set

from flaskprice.config import SUPPORTED_STREAMS

clients: Dict[str, Set[str]] = {stream: set() for stream in SUPPORTED_STREAMS}

queues: Dict[str, queue.Queue] = {stream: queue.Queue() for stream in SUPPORTED_STREAMS}
