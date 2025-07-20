from main.common.kafka_consumer import KafkaDataHandler


class PostgresKafkaDataHandler(KafkaDataHandler):
    def __init__(self, group_id, mapper, inserter_raw, inserter_processed, inserter_failed):
        self.group_id = group_id
        self.mapper = mapper
        self.inserter_raw = inserter_raw
        self.inserter_processed = inserter_processed
        self.inserter_failed = inserter_failed

    def handle(self, data):
        # self.inserter_raw.add(self.mapper.get_raw(data).values_insert()) # TODO: implement deleting data periodically
        try:
            self.inserter_processed.add(self.mapper.get_processed(data).values_insert())
        except Exception as e:
            self.inserter_failed.add(self.mapper.get_failed(data, e).values_insert())
