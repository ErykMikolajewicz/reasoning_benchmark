import os
from pathlib import Path
from typing import Any, Optional

from google.auth import default
from google.auth.transport.requests import Request
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.share.enums import ColorGenerator, Environment

BENCHMARK_SETTINGS_FILE_PATH = Path("settings") / "benchmark.env"
APPLICATION_SETTINGS_FILE_PATH = Path("settings") / "application.env"
ENGINE_SETTINGS_FILE_PATH = Path("settings") / "engine.env"


class EngineSettings(BaseSettings):
    ANALYSE_DEPTH: int
    MOVE_ACCEPTANCE_THRESHOLD_CENTI_PAWS: int
    MULTI_PV: int

    model_config = SettingsConfigDict(
        env_file=ENGINE_SETTINGS_FILE_PATH,
        env_file_encoding="utf-8",
        case_sensitive=True,
        frozen=False,
    )


class BenchmarkSettings(BaseSettings):
    BENCHMARKING_MODEL: str

    MAX_PLY: int
    MAX_ILLEGAL_MOVES: int

    STRATEGY: Optional[str] = None

    engine_settings: dict[str, int] = {}

    model_extra_config: dict[str, Any] = {}

    model_config = SettingsConfigDict(
        env_file=BENCHMARK_SETTINGS_FILE_PATH,
        env_file_encoding="utf-8",
        case_sensitive=True,
        frozen=False,
    )


class ApplicationSettings(BaseSettings):
    ENVIRONMENT: Environment
    LOGGING_LEVEL: Optional[str] = None

    PLAYS_NUMBER: int
    MAX_WORKERS: int

    COLOR_GENERATOR: ColorGenerator

    APPEND_RESULTS: bool

    RETRY_NUMBER: int
    LLM_TIMEOUT: Optional[int] = None
    MINIMUM_WAIT_SECONDS: int
    MAXIMUM_WAIT_SECONDS: int

    VERTEX_OPENAI_KEY: bool = False

    model_config = SettingsConfigDict(
        env_file=APPLICATION_SETTINGS_FILE_PATH,
        env_file_encoding="utf-8",
        case_sensitive=True,
        frozen=True,
    )


class Settings(BaseSettings):
    benchmark: BenchmarkSettings = BenchmarkSettings()
    application: ApplicationSettings = ApplicationSettings()
    engine: EngineSettings = EngineSettings()

    model_config = SettingsConfigDict(case_sensitive=True, frozen=True)


settings = Settings()

if settings.application.VERTEX_OPENAI_KEY:
    credentials, _ = default()
    credentials.refresh(Request())
    os.environ["OPENAI_API_KEY"] = credentials.token
