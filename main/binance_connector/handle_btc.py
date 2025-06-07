from main.binance_connector.data_handler import DataHandler, DataHandler
import time
import logging
from main.common.utils import default_logger

if __name__ == '__main__':
    logger = default_logger("main", logging.DEBUG) # write project's root module to propagate log config
    logger.info("BTC handling begins")
    dataHandler = DataHandler(symbol='btcusdt')
    dataHandler.start()
    dataHandler.mini_ticker()
    time.sleep(5)
    dataHandler.mini_ticker(action=DataHandler.ACTION_UNSUBSCRIBE)
    dataHandler.stop()