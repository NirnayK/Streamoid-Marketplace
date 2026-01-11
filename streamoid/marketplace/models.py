from django.db import models

from core.constants import MAX_NAME_LENGTH
from core.models import BaseModel


class Marketplace(BaseModel):
    name = models.CharField(max_length=MAX_NAME_LENGTH, db_index=True)
    # Future relevant fields related to marketplace


class MarketplaceTempate(BaseModel):
    marketplace = models.ForeignKey(Marketplace, on_delete=models.CASCADE)
    template = models.JSONField()
