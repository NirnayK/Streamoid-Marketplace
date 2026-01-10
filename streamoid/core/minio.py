from functools import lru_cache

from django.conf import settings
from minio import Minio


@lru_cache(maxsize=1)
def get_minio_client() -> Minio:
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
    )
