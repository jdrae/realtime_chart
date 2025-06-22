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
    def sql_insert(cls, table_name: str, bulk) -> str:
        cols = cls.cols_insert()
        placeholders = "%s"
        if not bulk:
            placeholders = "(" + ", ".join(["%s"] * len(cols)) + ")"
        col_str = ", ".join(cols)
        return f"INSERT INTO {table_name} ({col_str}) VALUES {placeholders}"

    def values_insert(self) -> tuple:
        return tuple(getattr(self, col) for col in self.cols_insert())


@dataclass
class Raw(Entity):
    payload: str
    id: Optional[str] = None
    received_at: Optional[str] = None

    EXCLUDE_INSERT_COLS = {"id", "received_at"}


@dataclass
class Failed(Entity):
    payload: str
    error: str
    id: Optional[str] = None
    received_at: Optional[str] = None

    EXCLUDE_INSERT_COLS = {"id", "received_at"}


@dataclass
class MiniTicker(Entity):
    event_time: str
    symbol: str
    close_price: str
    open_price: str
    high_price: str
    low_price: str
    volume_base: str
    volume_quote: str
    id: Optional[str] = None
    received_at: Optional[str] = None

    EXCLUDE_INSERT_COLS = {"id", "received_at"}
