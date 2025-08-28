import json
import logging.config

from src.share.settings import settings
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
    from google.cloud import logging as gcl
    client = gcl.Client()
    client.setup_logging()

    if LOGGING_LEVEL:
        logging.getLogger().setLevel(LOGGING_LEVEL)


def setup_logging():
    match ENVIRONMENT:
        case Environment.LOCAL:
            set_file_logging()
        case Environment.GOOGLE_CLOUD:
            set_google_cloud_logging()
        case _:
            raise RuntimeError(f"Unknown environment: {ENVIRONMENT}")
