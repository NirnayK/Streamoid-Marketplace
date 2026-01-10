import uuid

from django.db import models

from core.constants import MAX_NAME_LENGTH
from core.models import BaseModel
from seller.constants import MAX_FILE_PATH_LENGTH


class ContentType(models.TextChoices):
    CSV = "csv", "CSV"
    XLSX = "xlsx", "Excel"


class Seller(BaseModel):
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    bucket_name = models.UUIDField(default=uuid.uuid4)

    def __str__(self):
        return f"<Seller: {self.id} | Name: {self.name} | Bucket Name: {self.bucket_name}"


class SellerFiles(BaseModel):
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL)

    name = models.CharField(max_length=MAX_NAME_LENGTH)
    type = models.CharField(max_length=MAX_NAME_LENGTH, choices=ContentType.choices)
    path = models.CharField(max_length=MAX_FILE_PATH_LENGTH)

    rows_count = models.IntegerField(default=0)
    headers = models.JSONField(default=list)
    sample_rows = models.JSONField(default=list)

    def __str__(self):
        return f"<SellerFiles: {self.id} | Rows Count: {self.rows_count} | Path: {self.path} "
