import logging
import queue
import threading
import time
from datetime import datetime

from psycopg2 import pool
from psycopg2.extras import execute_values


class PostgresClient:
    def __init__(self):  # TODO: dsn
        self.logger = logging.getLogger(__name__ + ".PostgresClient")
        self.pool = None

    def connect(self, dbname, user, password, host, port):
        self.logger.info("Connecting to Postgres")
        self.pool = pool.ThreadedConnectionPool(
            minconn=3, maxconn=6, dbname=dbname, user=user, password=password, host=host, port=port
        )
        self.logger.info("Connected to Postgres")

    def insert_one(self, query: str, data: tuple):
        conn = self.pool.getconn()
        try:
            cursor = conn.cursor()
            cursor.execute(query, data)
            conn.commit()
        finally:
            self.pool.putconn(conn)

    def insert_many(self, query: str, data: list[tuple]):
        conn = self.pool.getconn()
        try:
            cursor = conn.cursor()
            execute_values(cursor, query, data)
            conn.commit()
            self.logger.debug(f"Inserted {len(data)} records with query: {query}")
        finally:
            self.pool.putconn(conn)

    def close(self):
        self.logger.debug("Closing Postgres connection")
        self.pool.closeall()
        self.logger.debug("Postgres connection closed")


class BatchInserter:
    def __init__(self, db_client, query, max_batch_size, flush_worker=False, checkpoint_handler=None):
        self.logger = logging.getLogger(__name__ + ".BatchInserter")

        self.db_client = db_client
        self.query = query
        self.max_batch_size = max_batch_size
        self.flush_worker = flush_worker
        self.checkpoint_handler = checkpoint_handler

        self.buffer = []
        self.lock = threading.Lock()
        self.flush_queue = queue.Queue()
        self.running = None
        self.flush_thread = None
        self.insert_thread = None

    def start(self):
        self.logger.info("Starting BatchInserter...")
        self.running = True
        if self.flush_worker:
            self.flush_thread = threading.Thread(target=self._flush_worker, daemon=True)
            self.flush_thread.start()
        self.insert_thread = threading.Thread(target=self._insert_worker, daemon=False)
        self.insert_thread.start()
        self.logger.info("BatchInserter started")

    def add(self, data: tuple):
        # data is mapped and converted as insert value from data handler
        with self.lock:
            self.buffer.append(data)
            if len(self.buffer) >= self.max_batch_size:
                self._flush()

    def _flush(self):
        if not self.buffer:
            return
        batch = self.buffer[:]
        self.buffer.clear()
        self.flush_queue.put(batch)

    def _flush_worker(self):
        padding = 2  # flush every *m 2s
        while self.running:
            now = int(datetime.now().timestamp())
            target = int(datetime.now().replace(second=0, microsecond=0).timestamp()) + 60 + padding
            sleep_duration = target - now
            time.sleep(sleep_duration)
            with self.lock:
                self._flush()

    def _insert_worker(self):
        while self.running or not self.flush_queue.empty():
            try:
                # queue timeout is necessary when process ended without any data
                batch = self.flush_queue.get(timeout=3)
                self.db_client.insert_many(self.query, batch)
                if self.checkpoint_handler:
                    self.checkpoint_handler.insert_checkpoint(batch)
            except queue.Empty:
                continue

    def stop(self):
        self.logger.info("Stopping BatchInserter...")
        with self.lock:
            self._flush()
        self.running = False
        self.flush_thread.join()
        self.insert_thread.join()
        self.logger.info("BatchInserter stopped")
