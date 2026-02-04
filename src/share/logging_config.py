import json
import logging.config

from src.settings import settings
from src.share.enums import Environment

LOGGING_LEVEL = settings.application.LOGGING_LEVEL
ENVIRONMENT = settings.application.ENVIRONMENT


def set_file_logging():
    with open("settings/logging.json") as f:
        config = json.load(f)

    if LOGGING_LEVEL:
        config["loggers"]["src"]["level"] = LOGGING_LEVEL
    logging.config.dictConfig(config)


def set_google_cloud_logging():
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {"default": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"}},
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            }
        },
        "root": {"level": "WARNING", "handlers": ["console"]},
        "loggers": {"src": {"level": "INFO", "handlers": ["console"], "propagate": False}},
    }

    if LOGGING_LEVEL:
        config["loggers"]["src"]["level"] = LOGGING_LEVEL
    logging.config.dictConfig(config)


def setup_logging():
    match ENVIRONMENT:
        case Environment.LOCAL:
            set_file_logging()
        case Environment.GOOGLE_CLOUD:
            set_google_cloud_logging()
        case _:
            raise RuntimeError(f"Unknown environment: {ENVIRONMENT}")
