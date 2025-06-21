import logging

import psycopg2
from psycopg2.extras import RealDictCursor


class PostgresClient:
    def __init__(self, dbname, user, password, host, port):
        self.logger = logging.getLogger(__name__)

        self.logger.info("Connecting to Postgres")
        self.conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        self.logger.info("Connected to Postgres")

    def insert_raw_data(self, table, data):
        cols = ", ".join(["source", "payload"])
        placeholders = ", ".join(["%s", "%s"])
        values = tuple(["binance_miniticker", data])
        query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        self.cursor.execute(query, values)
        self.conn.commit()

    def fetch_all(self, query, params=None):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def close(self):
        self.logger.debug("Closing Postgres connection")
        self.cursor.close()
        self.conn.close()
        self.logger.debug("Postgres connection closed")
