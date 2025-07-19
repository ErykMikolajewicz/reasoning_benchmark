import json
import logging.config

from src.share.settings import settings

with open("settings/logging.json") as f:
    config = json.load(f)

LOGGING_LEVEL = settings.application.LOGGING_LEVEL
if LOGGING_LEVEL:
    config["loggers"]["src"]["level"] = LOGGING_LEVEL


def setup_logging():
    logging.config.dictConfig(config)
