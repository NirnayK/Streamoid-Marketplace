import os

from core.constants import LOCAL, PRODUCTION

env = os.getenv("DJANGO_ENV", LOCAL).lower()

if env == PRODUCTION:
    from config.settings.production import *  # noqa: F403, F401
else:
    from config.settings.local import *  # noqa: F403, F401
