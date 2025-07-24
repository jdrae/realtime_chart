from django.db import models


class CheckpointEnum(models.IntegerChoices):
    PENDING = 0, "Pending"
    AGGREGATED = 1, "Aggregated"
    ERROR = 2, "Error"
