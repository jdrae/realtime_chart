from dataclasses import fields
from typing import List, Optional, ClassVar

from pydantic.dataclasses import dataclass


@dataclass
class Entity:
    EXCLUDE_INSERT_COLS: ClassVar[set]

    @classmethod
    def cols_insert(cls) -> List[str]:
        """
        The order of the fields in all of the generated methods is the order in which they appear in the class definition.
        https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass
        """
        return [f.name for f in fields(cls) if f.name not in cls.EXCLUDE_INSERT_COLS]

    @classmethod
    def sql_insert(cls, table_name: str) -> str:
        cols = cls.cols_insert()
        placeholders = "%s"
        col_str = ", ".join(cols)
        return f"INSERT INTO {table_name} ({col_str}) VALUES {placeholders}"

    def values_insert(self) -> tuple:
        return tuple(getattr(self, col) for col in self.cols_insert())


@dataclass
class Raw(Entity):
    payload: str
    id: Optional[str] = None
    created_at: Optional[str] = None

    EXCLUDE_INSERT_COLS = {"id", "created_at"}


@dataclass
class Failed(Entity):
    payload: str
    error: str
    id: Optional[str] = None
    created_at: Optional[str] = None

    EXCLUDE_INSERT_COLS = {"id", "created_at"}


@dataclass
class MiniTicker(Entity):
    event_time: int
    symbol: str
    open_price: str
    close_price: str
    high_price: str
    low_price: str
    volume_base: str
    volume_quote: str

    id: Optional[str] = None
    created_at: Optional[str] = None
    EXCLUDE_INSERT_COLS = {"id", "created_at"}


@dataclass
class Kline(Entity):
    event_time: int
    symbol: str
    is_closed: bool
    start_time: int
    close_time: int
    first_trade_id: int
    last_trade_id: int
    open_price: str
    close_price: str
    high_price: str
    low_price: str
    trade_count: int
    volume_base: str
    volume_quote: str
    taker_volume_base: str
    taker_volume_quote: str

    id: Optional[str] = None
    created_at: Optional[str] = None
    EXCLUDE_INSERT_COLS = {"id", "created_at"}


@dataclass
class AggregatedKlineCheckpoint(Entity):
    symbol: str
    first_time: int
    last_time: int
    is_1m_aggregated: Optional[bool] = None
    is_5m_aggregated: Optional[bool] = None
    is_15m_aggregated: Optional[bool] = None

    id: Optional[str] = None
    created_at: Optional[str] = None
    EXCLUDE_INSERT_COLS = {
        "id",
        "created_at",
        "is_1m_aggregated",
        "is_5m_aggregated",
        "is_15m_aggregated",
    }
