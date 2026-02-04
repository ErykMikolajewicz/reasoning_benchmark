import json
import logging.config

from domain.enums import Environment
from share.settings.app import application_settings

LOGGING_LEVEL = application_settings.LOGGING_LEVEL
ENVIRONMENT = application_settings.ENVIRONMENT


def set_file_logging():
    with open("logging.json") as f:
        config = json.load(f)

    if LOGGING_LEVEL:
        config["loggers"]["domain"]["level"] = LOGGING_LEVEL
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
