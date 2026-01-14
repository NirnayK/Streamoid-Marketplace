from functools import lru_cache

from django.conf import settings
from loguru import logger
from minio import Minio

log = logger.bind(component="minio")


class MinioHandler:
    def __init__(self, client: Minio | None = None) -> None:
        self.client = client or self._get_client()

    @staticmethod
    @lru_cache(maxsize=1)
    def _get_client() -> Minio:
        return Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )

    def check_and_create_bucket(self, bucket_name):
        if not self.client.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name=bucket_name)
            log.info("Created MinIO bucket: {}", bucket_name)
        else:
            log.debug("MinIO bucket exists: {}", bucket_name)

    def store_file(self, bucket_name, file_name, file):
        try:
            self.check_and_create_bucket(bucket_name)
        except Exception as e:
            log.exception(f"Failed to ensure MinIO bucket exists: {bucket_name} | Error: {e}")
            return False
        log.info("Storing object in MinIO: bucket={}, object={}", bucket_name, file_name)
        try:
            self.client.put_object(bucket_name=bucket_name, object_name=file_name, data=file, length=file.size)
        except Exception as e:
            log.exception(f"Falied to upload file | Error: {e}")
            return False
        return True

    def remove_file(self, bucket_name, file_name):
        log.info("Removing object from MinIO: bucket={}, object={}", bucket_name, file_name)
        try:
            self.client.remove_object(bucket_name=bucket_name, object_name=file_name)
        except Exception as e:
            log.exception(f"Failed to remove file | Error: {e}")
            return False
        return True

    def get_file(self, bucket_name, file_name):
        try:
            file_object = self.client.get_object(bucket_name, file_name)
            return file_object
        except Exception as e:
            log.exception(f"Failed to fetch file | Error: {e}")
            return None
