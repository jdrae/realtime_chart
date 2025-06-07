import time
import logging
import json

def get_timestamp():
    return int(time.time() * 1000)

def default_logger(name, log_level):
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.addHandler(_console_handler())
    # logger.addHandler(_file_handler())
    return logger

def _plain_formatter():
    return logging.Formatter('%(asctime)s %(levelname)s\t%(name)s \t %(message)s')

def _console_handler():
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(_plain_formatter())
    return handler

def _file_handler():
    formatter = JsonFormatter()
    handler = logging.FileHandler('log.log') # TODO: log save file
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    return handler

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'time': record.asctime,
            'name': record.name,
            'level': record.levelname,
            'message': record.msg
        }
        return json.dumps(log_data)

class JsonLogMessage(dict):
    def __init__(self, message, *arg, **kw):
        kw.update({"message":message})
        super(JsonLogMessage, self).__init__(*arg, **kw)
