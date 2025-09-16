# server/config/base.py
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Server Settings
HOST = os.getenv("GAME_SERVER_HOST", "127.0.0.1")
PORT = int(os.getenv("GAME_SERVER_PORT", 5000))

# Database
DB_URI = os.getenv("GAME_DB_URI", f"sqlite:///{BASE_DIR / 'db' / 'game.db'}")

# Logging
LOG_LEVEL = os.getenv("GAME_LOG_LEVEL", "INFO")

# Gameplay Defaults
TICK_RATE = 30
MAX_PLAYERS = 100
