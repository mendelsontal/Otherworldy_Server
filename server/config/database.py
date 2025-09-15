# DB configs

import os
from . import settings

# Default DB (override via environment variable)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{settings.BASE_DIR}/game.db")
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 5))
