import json
from abc import abstractmethod

from main.common.entity import *


def get_json_entity_mapper(target_entity):
    target_entity = target_entity.upper()
    if target_entity == "MINITICKER":
        return MiniTickerEntityMapper()
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
    def get_processed(self, data: str):
        pass


class MiniTickerEntityMapper(JsonEntityMapper):

    def get_processed(self, data: str) -> MiniTicker:
        data = json.loads(str(data))["data"]
        return MiniTicker(
            event_time=str(data["E"]),
            symbol=data["s"],
            close_price=data["c"],
            open_price=data["o"],
            high_price=data["h"],
            low_price=data["l"],
            volume_base=data["v"],
            volume_quote=data["q"],
        )
