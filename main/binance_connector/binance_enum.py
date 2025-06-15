from enum import Enum

class StreamName(Enum):
    MINI_TICKER = "{}@miniTicker"
    KLINE_1M = "{}@kline_1m"

class Symbol(Enum):
    BTCUSDT = "btcusdt"
    ETHUSDT = "ethusdt"