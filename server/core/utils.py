# server/core/utils.py
import time
import random
import string
import logging

def setup_logger(name: str, level=logging.INFO):
    """Simple logger setup."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger

def generate_id(length=8):
    """Generate a random alphanumeric ID."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def current_timestamp():
    """Return current UNIX timestamp."""
    return int(time.time())
