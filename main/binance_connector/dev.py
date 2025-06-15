import logging
import time

from main.binance_connector.binance_enum import Symbol, StreamName
from main.binance_connector.data_handler import DataHandler
from main.common.utils import default_logger

if __name__ == '__main__':
    logger = default_logger("main", logging.DEBUG) # write project's root module to propagate log config
    dataHandler = DataHandler(stream_name=StreamName.MINI_TICKER,
                              symbols=[Symbol.BTCUSDT, Symbol.ETHUSDT])
    dataHandler.start()
    time.sleep(5)
    dataHandler.stop()