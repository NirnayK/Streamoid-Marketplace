from pathlib import Path

from django.db import models

from core.constants import MAX_NAME_LENGTH
from core.minio import MinioHandler
from core.models import BaseModel
from mapping.constants import EVALUATION_STATUS_CHOICES, EVALUATION_STATUS_PENDING, TRANSFORMED_FOLDER
from marketplace.models import MarketplaceTempate
from seller.constants import MAX_FILE_PATH_LENGTH
from seller.models import SellerFiles


class Mappings(BaseModel):
    marketplace_template = models.ForeignKey(MarketplaceTempate, on_delete=models.CASCADE)
    seller_file = models.ForeignKey(SellerFiles, on_delete=models.CASCADE)
    mappings = models.JSONField(default=dict)
    evaluation_status = models.CharField(
        max_length=MAX_NAME_LENGTH,
        choices=EVALUATION_STATUS_CHOICES,
        default=EVALUATION_STATUS_PENDING,
    )
    transformed_file_path = models.CharField(max_length=MAX_FILE_PATH_LENGTH, null=True, blank=True, default=None)

    def __str__(self):
        return (
            f"<Mappings: {self.id} | Marketplace Template: {self.marketplace_template_id} "
            f"| Seller File: {self.seller_file_id}"
        )

    @property
    def transformed_file(self):
        bucket_name = self.seller_file.seller.bucket_name
        file_name = str(Path(TRANSFORMED_FOLDER).joinpath(self.seller_file.name))
        return MinioHandler().get_file(bucket_name, file_name)
