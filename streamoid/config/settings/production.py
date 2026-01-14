import os
from pathlib import Path

from dotenv import load_dotenv

from config import settings_base as base
from config.settings_base import *  # noqa: F403, F401

load_dotenv(base.BASE_DIR / ".env")
load_dotenv(Path("/run/secrets/app_env"), override=True)


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY is required in production.")

DEBUG = base.env_bool("DJANGO_DEBUG", False)
ALLOWED_HOSTS = base.env_list("DJANGO_ALLOWED_HOSTS", default=[])

LOG_DIR = Path(os.getenv("LOG_DIR", "/var/log/streamoid"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
base.init_logging(LOG_DIR, LOG_LEVEL)

# Database configuration for production (MySQL)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "HOST": os.getenv("MYSQL_HOST", "mysql"),
        "PORT": os.getenv("MYSQL_PORT", "3306"),
        "NAME": os.getenv("MYSQL_DATABASE", "streamoid"),
        "USER": os.getenv("MYSQL_USER", "streamoid"),
        "PASSWORD": os.getenv("MYSQL_PASSWORD", "streamoid"),
    }
}
