from abc import abstractmethod
from collections import deque

from pythonprice.common.entity import AggregatedKline, Indicator


class IndicatorCalculator:
    @abstractmethod
    def calculate(self, data: AggregatedKline):
        pass

    @abstractmethod
    def get_indicator(self, data: AggregatedKline) -> Indicator:
        pass


class MovingAverageCalculator(IndicatorCalculator):
    def __init__(self, interval, period):
        self.label = "ma_{}".format(period)
        self.interval = interval
        self.period = period
        self.close_prices = deque(maxlen=period)
        self.sum = 0.0

    def calculate(self, data: AggregatedKline):
        price = data.close_price
        if len(self.close_prices) == self.period:
            self.sum -= self.close_prices[0]
        self.close_prices.append(price)
        self.sum += price

        if len(self.close_prices) == self.period:
            return self.sum / self.period
        else:
            return None

    def get_indicator(self, data: AggregatedKline) -> Indicator:
        value = self.calculate(data)
        return Indicator(
            symbol=data.symbol,
            interval=data.interval,
            start_time=data.start_time,
            label=self.label,
            value=value,
        )
