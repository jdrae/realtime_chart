import logging
from abc import ABC, abstractmethod
from collections import defaultdict

from main.common.entity import AggregatedKlineCheckpoint


class CheckpointHandler(ABC):
    def __init__(self, db_client, table: str):
        self.logger = logging.getLogger(__name__)
        self.db_client = db_client
        self.table = table

    @abstractmethod
    def insert_checkpoint(self, batch: list[dict]):
        pass


class KlineCheckpointHandler(CheckpointHandler):

    def __init__(self, db_client, table: str):
        super().__init__(db_client, table)
        self.query = AggregatedKlineCheckpoint.sql_insert(table)

    def insert_checkpoint(self, batch: list[dict]):
        checkpoint_state = defaultdict(list)
        for data in batch:
            # data order is same as entity column order
            # checkpoint_state[symbol].extend([start_time, close_time])
            checkpoint_state[data[1]].extend([data[3], data[4]])

        checkpoint_row = []
        for symbol, times in checkpoint_state.items():
            first_time = min(times)
            last_time = max(times)
            checkpoint_row.append(
                AggregatedKlineCheckpoint(
                    symbol=symbol,
                    first_time=first_time,
                    last_time=last_time,
                ).values_insert()
            )

        self.logger.debug(checkpoint_row)
        self.db_client.insert_many(self.query, checkpoint_row)
