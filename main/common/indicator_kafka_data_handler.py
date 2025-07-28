from main.common.entity import Failed, Indicator
from main.common.entity_mapper import AggregatedKlineEntityMapper
from main.common.indicator import IndicatorCalculator
from main.common.kafka_consumer import KafkaDataHandler


class IndicatorKafkaDataHandler(KafkaDataHandler):
    def __init__(
        self,
        group_id,
        db_client,
        indicators: dict[str, list[IndicatorCalculator]],
        fail_table,
        processed_table,
    ):
        super().__init__(group_id)
        self.db_client = db_client
        self.indicators = indicators
        self.processed_query = Indicator.sql_insert(processed_table)
        self.fail_query = Failed.sql_insert(fail_table)
        self.mapper = AggregatedKlineEntityMapper()

    def handle(self, data: str):
        try:
            calculated = []  # list of tuples
            aggregated_kline = self.mapper.get_processed(data)
            indicators = self.indicators[aggregated_kline.symbol]
            for indicator in indicators:
                calculated.append(indicator.calculate(aggregated_kline).values_insert())
            self.db_client.insert_many(self.processed_query, calculated)
        except Exception as e:
            self.db_client.insert_one(self.fail_query, self.mapper.get_failed(data, e))
