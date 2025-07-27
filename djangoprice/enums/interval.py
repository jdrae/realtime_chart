from enum import Enum


class Interval(Enum):
    _1m = ("1m", "is_1m_aggregated", 60)
    _5m = ("5m", "is_5m_aggregated", 300)
    _15m = ("15m", "is_15m_aggregated", 900)

    def __init__(self, label, column, seconds):
        self.label = label
        self.column = column
        self.seconds = seconds

    def __repr__(self):
        return self.label

    def __str__(self):
        return self.label

    @classmethod
    def from_label(cls, label):
        for member in cls:
            if member.label == label:
                return member
        raise ValueError(f"No matching Color for label: {label}")
