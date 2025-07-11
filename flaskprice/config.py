KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
SOCKETIO_HOST = "localhost"
SOCKETIO_PORT = 5555
CORS_ORIGINS = "*"
KAFKA_TOPIC = "kline_1s"
KAFKA_GROUP_ID = "kline_1s_flask"
SUPPORTED_STREAMS = ["btcusdt", "ethusdt", "xrpusdt"]  # used as 'streams' variable
SYMBOL_TO_STREAM = {"BTCUSDT": "btcusdt", "ETHUSDT": "ethusdt", "XRPUSDT": "xrpusdt"}
