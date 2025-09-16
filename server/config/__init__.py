import os
env = os.getenv("ENV", "development")

if env == "production":
    from .production import *
elif env == "test":
    from .test import *
else:
    from .development import *
