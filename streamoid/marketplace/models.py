from django.db import models

from core.constants import MAX_NAME_LENGTH
from core.models import BaseModel


class Marketplace(BaseModel):
    name = models.CharField(max_length=MAX_NAME_LENGTH, db_index=True)
    # Future relevant fields related to marketplace

    def __str__(self):
        return f"<Marketplace: {self.id} | Name: {self.name}"


class MarketplaceTempate(BaseModel):
    marketplace = models.ForeignKey(Marketplace, on_delete=models.CASCADE)
    template = models.JSONField(default=dict)

    def __str__(self):
        return f"<MarketplaceTempate: {self.id} | Marketplace: {self.marketplace_id}"
