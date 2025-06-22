import logging
import queue
import threading

from psycopg2 import pool
from psycopg2.extras import execute_values


class MockPostgresClient:
    def __init__(self):
        pass

    def connect(self, dbname, user, password, host, port):  # TODO: dsn
        print("connected")

    def insert_many(self, query: str, data: list[tuple]):
        print(query, len(data))

    def close(self):
        print("db closed")


class PostgresClient:
    def __init__(self):  # TODO: dsn
        self.logger = logging.getLogger(__name__ + ".PostgresClient")
        self.pool = None

    def connect(self, dbname, user, password, host, port):
        self.logger.info("Connecting to Postgres")
        self.pool = pool.ThreadedConnectionPool(
            minconn=3, maxconn=3, dbname=dbname, user=user, password=password, host=host, port=port
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
    def __init__(self, db_client, query, batch_size):
        self.logger = logging.getLogger(__name__ + ".BatchInserter")

        self.db_client = db_client
        self.query = query
        self.batch_size = batch_size

        self.buffer = []
        self.lock = threading.Lock()
        self.flush_queue = queue.Queue()
        self.running = None
        self.insert_thread = None

    def start(self):
        self.logger.info("Starting BatchInserter...")
        self.running = True
        self.insert_thread = threading.Thread(target=self._insert_worker, daemon=False)
        self.insert_thread.start()
        # TODO: implement flush_thread to check last flush time
        self.logger.info("BatchInserter started")

    def add(self, data: dict):
        with self.lock:
            self.buffer.append(data)
            if len(self.buffer) >= self.batch_size:
                self._flush()

    def _flush(self):
        if not self.buffer:
            return
        batch = self.buffer[:]
        self.buffer.clear()
        self.flush_queue.put(batch)

    def _insert_worker(self):
        while self.running or not self.flush_queue.empty():
            try:
                batch = self.flush_queue.get(timeout=1)  # if timeout=None, wait until an item is available.
                self.db_client.insert_many(self.query, batch)
            except queue.Empty:
                continue

    def stop(self):
        with self.lock:
            self._flush()

        self.logger.info("Stopping BatchInserter...")
        self.running = False
        self.insert_thread.join()
        self.logger.info("BatchInserter stopped")
