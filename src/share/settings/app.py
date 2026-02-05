import os

from pydantic_settings import BaseSettings, SettingsConfigDict

from domain.enums import ColorGenerator
from share.enums import Environment


class ApplicationSettings(BaseSettings):
    ENVIRONMENT: Environment = ...
    LOGGING_LEVEL: str | None = None

    MODEL_PROVIDER: str

    PLAYS_NUMBER: int = ...
    MAX_WORKERS: int = ...

    COLOR_GENERATOR: ColorGenerator = ...

    APPEND_RESULTS: bool = ...

    RETRY_NUMBER: int = ...
    LLM_TIMEOUT: int | None = None
    MINIMUM_WAIT_SECONDS: int = ...
    MAXIMUM_WAIT_SECONDS: int = ...

    VERTEX_OPENAI_KEY: bool = False

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", env_prefix="APP_", case_sensitive=True, frozen=True, extra="ignore"
    )


application_settings = ApplicationSettings()

if application_settings.VERTEX_OPENAI_KEY:
    from google.auth import default
    from google.auth.transport.requests import Request

    credentials, _ = default()
    credentials.refresh(Request())
    os.environ["OPENAI_API_KEY"] = credentials.token
