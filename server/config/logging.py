# server/config/logging.py
import logging
import logging.handlers
import os
from .base import LOG_LEVEL, BASE_DIR

LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
log_file = os.path.join(LOGS_DIR, "server.log")

level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    log_file, maxBytes=5*1024*1024, backupCount=5, encoding="utf-8"
)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(level)
logger.addHandler(handler)

# Console output
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
