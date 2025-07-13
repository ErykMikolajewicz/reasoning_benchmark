import json
import logging.config

from src.share.settings import settings

with open("logging.json") as f:
    config = json.load(f)

LOGGING_LEVEL = settings.application.LOGGING_LEVEL


def setup_logging():
    logging.config.dictConfig(config)
    if LOGGING_LEVEL:
        config["loggers"]["src"]["level"] = LOGGING_LEVEL

    for name in logging.root.manager.loggerDict:
        print(name)
