import os

from streamoid.core.constants import PRODUCTION

env = os.getenv("DJANGO_ENV", "local").lower()

if env == PRODUCTION:
    from settings.production import *  # noqa: F403, F401
else:
    from settings.local import *  # noqa: F403, F401
