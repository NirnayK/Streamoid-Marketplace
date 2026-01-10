import uuid

from django.db import models

from streamoid.core.constants import MAX_NAME_LENGTH
from streamoid.core.models import BaseModel
from streamoid.seller.constants import MAX_FILE_PATH_LENGTH


class ContentType(models.TextChoices):
    CSV = "csv", "CSV"
    XLSX = "xlsx", "Excel"


class Seller(BaseModel):
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    path_uuid = models.UUIDField(default=uuid.uuid4)


class SellerFiles(BaseModel):
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL)
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    type = models.CharField(max_length=MAX_NAME_LENGTH, choices=ContentType.choices)
    path = models.CharField(max_length=MAX_FILE_PATH_LENGTH)
    headers = models.JSONField(default=list)
    rows_count = models.IntegerField(default=0)
