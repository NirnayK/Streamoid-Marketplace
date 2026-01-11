from django.db import models

from core.models import BaseModel
from marketplace.models import MarketplaceTempate
from seller.models import SellerFiles


class Mappings(BaseModel):
    marketplace_template = models.ForeignKey(MarketplaceTempate, on_delete=models.CASCADE)
    seller_file = models.ForeignKey(SellerFiles, on_delete=models.CASCADE)
    mappings = models.JSONField(default=dict)

    def __str__(self):
        return (
            f"<Mappings: {self.id} | Marketplace Template: {self.marketplace_template_id} "
            f"| Seller File: {self.seller_file_id}"
        )
