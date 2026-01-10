from functools import lru_cache

from django.conf import settings
from loguru import logger
from minio import Minio

log = logger.bind(component="minio")


@lru_cache(maxsize=1)
def get_minio_client() -> Minio:
    return Minio(
        settings.MINIO_ENDPOINT,
        access_key=settings.MINIO_ACCESS_KEY,
        secret_key=settings.MINIO_SECRET_KEY,
    )


def check_and_create_bucket(self, bucket_name):
    client = get_minio_client()
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name=bucket_name)
        log.info("Created MinIO bucket: {}", bucket_name)
    else:
        log.debug("MinIO bucket exists: {}", bucket_name)


def minio_store_file(bucket_name, file_name, file):
    client = get_minio_client()
    try:
        check_and_create_bucket(bucket_name)
    except Exception as e:
        log.exception(f"Failed to ensure MinIO bucket exists: {bucket_name} | Error: {e}")
        return False
    log.info("Storing object in MinIO: bucket={}, object={}", bucket_name, file_name)
    try:
        client.append_object(bucket_name=bucket_name, file_name=file_name, data=file)
    except Exception as e:
        log.exception(f"Falied to upload file | Error: {e}")
        return False
    return True


def minio_remove_file(bucket_name, file_name):
    client = get_minio_client()
    log.info("Removing object from MinIO: bucket={}, object={}", bucket_name, file_name)
    try:
        client.remove_object(bucket_name=bucket_name, object_name=file_name)
    except Exception as e:
        log.exception(f"Failed to remove file | Error: {e}")
        return False
    return True
