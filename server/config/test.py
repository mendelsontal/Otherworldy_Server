# overrides for tests

from .base import BaseConfig

class TestConfig(BaseConfig):
    ENV = "test"
    DEBUG = True
    # For testing you might use an in-memory DB
    DATABASE_URL = "sqlite:///:memory:"
