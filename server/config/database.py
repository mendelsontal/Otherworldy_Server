# server/config/database.py
import os
from .base import DB_URI

# Default DB URL (can override via environment)
DATABASE_URL = os.getenv("DATABASE_URL", DB_URI)
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 5))
