# overrides for dev

from .base import BaseConfig

class DevelopmentConfig(BaseConfig):
    ENV = "development"
    DEBUG = True
