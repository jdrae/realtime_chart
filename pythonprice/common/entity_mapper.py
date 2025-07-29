import json
from abc import abstractmethod

from pythonprice.common.entity import *


def get_json_entity_mapper(target_entity):
    target_entity = target_entity.upper()
    if target_entity == "MINITICKER":
        return MiniTickerEntityMapper()
    elif target_entity == "KLINE_1S":
        return KlineEntityMapper()
    else:
        raise NameError


class JsonEntityMapper:

    def get_raw(self, data) -> Raw:
        return Raw(
            payload=str(data),
        )

    def get_failed(self, data, e: Exception) -> Failed:
        return Failed(
            payload=str(data),
            error=str(e),
        )

    @abstractmethod
    def get_target_class(self):
        pass

    @abstractmethod
    def get_processed(self, data: str):
        pass


class MiniTickerEntityMapper(JsonEntityMapper):

    def get_target_class(self):
        return MiniTicker

    def get_processed(self, data: str) -> MiniTicker:
        data = json.loads(str(data))["data"]
        return MiniTicker(
            event_time=data["E"],
            symbol=data["s"],
            close_price=data["c"],
            open_price=data["o"],
            high_price=data["h"],
            low_price=data["l"],
            volume_base=data["v"],
            volume_quote=data["q"],
        )


class KlineEntityMapper(JsonEntityMapper):

    def get_target_class(self):
        return Kline

    def get_processed(self, data: str) -> Kline:
        data = json.loads(str(data))["data"]
        return Kline(
            event_time=data["E"],
            symbol=data["s"],
            is_closed=data["k"]["x"],
            start_time=data["k"]["t"],
            close_time=data["k"]["T"],
            first_trade_id=data["k"]["f"],
            last_trade_id=data["k"]["L"],
            open_price=data["k"]["o"],
            close_price=data["k"]["c"],
            high_price=data["k"]["h"],
            low_price=data["k"]["l"],
            trade_count=data["k"]["n"],
            volume_base=data["k"]["v"],
            volume_quote=data["k"]["q"],
            taker_volume_base=data["k"]["V"],
            taker_volume_quote=data["k"]["Q"],
        )


class AggregatedKlineEntityMapper(JsonEntityMapper):

    def get_target_class(self):
        return AggregatedKline

    def get_processed(self, data: str) -> AggregatedKline:
        data = json.loads(str(data))
        return AggregatedKline(
            interval=data["interval"],
            symbol=data["id"],
            start_time=data["start_time"],
            close_time=data["close_time"],
            open_price=data["open_price"],
            close_price=data["close_price"],
            high_price=data["high_price"],
            low_price=data["low_price"],
            trade_count=data["trade_count"],
            volume_base=data["volume_base"],
            volume_quote=data["volume_quote"],
            taker_volume_base=data["taker_volume_base"],
            taker_volume_quote=data["taker_volume_quote"],
        )
