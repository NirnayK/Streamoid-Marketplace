from django.db import models

from streamoid.core.constants import MAX_NAME_LENGTH
from streamoid.core.models import BaseModel


class ContentType(models.TextChoices):
    CSV = "csv", "CSV"
    XLSX = "xlsx", "Excel"


class Seller(BaseModel):
    name = models.CharField(max_length=MAX_NAME_LENGTH)


class SellerFiles(BaseModel):
    seller = models.ForeignKey(Seller, on_delete=models.SET_NULL)
    name = models.CharField(max_length=MAX_NAME_LENGTH)
    type = models.CharField(max_length=MAX_NAME_LENGTH, choices=ContentType.choices)
