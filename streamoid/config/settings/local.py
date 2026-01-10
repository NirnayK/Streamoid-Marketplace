# ruff: noqa: F403
import os

from dotenv import load_dotenv

from . import settings_base as base
from .settings_base import *  # noqa: F403, F401

load_dotenv(base.BASE_DIR / ".env.local")

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-i*82p@2(y@e9mpq^zic)rh*h&^4z87o8i%$3jegcibhd6sz=_d",
)
DEBUG = base.env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = base.env_list("DJANGO_ALLOWED_HOSTS", default=[])

LOG_DIR = base.BASE_DIR / "logs"
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
base.init_logging(LOG_DIR, LOG_LEVEL)
