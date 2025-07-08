import json
import logging.config

from src.settings import settings

with open("logging.json") as f:
    config = json.load(f)

LOGGING_LEVEL = settings.application.LOGGING_LEVEL
if LOGGING_LEVEL:
    config["root"]["level"] = LOGGING_LEVEL

def setup_logging():
    logging.config.dictConfig(config)
