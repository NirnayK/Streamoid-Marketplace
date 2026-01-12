import uuid
from pathlib import Path

from django.db import models

from core.constants import MAX_NAME_LENGTH
from core.minio import MinioHandler
from core.models import BaseModel
from seller.constants import MAX_FILE_PATH_LENGTH


class ContentType(models.TextChoices):
    CSV = "csv", "CSV"
    XLSX = "xlsx", "Excel"


class Seller(BaseModel):
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    bucket_name = models.UUIDField(default=uuid.uuid4)
    # Future relevant fields related to the seller

    def __str__(self):
        return f"<Seller: {self.id} | Name: {self.name} | Bucket Name: {self.bucket_name}"


class SellerFiles(BaseModel):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=MAX_NAME_LENGTH)
    type = models.CharField(max_length=MAX_NAME_LENGTH, choices=ContentType.choices)
    path = models.CharField(max_length=MAX_FILE_PATH_LENGTH)

    rows_count = models.IntegerField(default=0)
    headers = models.JSONField(default=list, blank=True)
    sample_rows = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"<SellerFiles: {self.id} | Rows Count: {self.rows_count} | Path: {self.path} "

    @property
    def file(self):
        bucket_name = Path(self.path).parent.name
        file_name = self.name
        return MinioHandler().get_file(bucket_name, file_name)
