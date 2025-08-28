from pathlib import Path
from typing import Optional, Any

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.share.enums import ColorGenerator, Environment

BENCHMARK_SETTINGS_FILE_PATH = Path("settings") / "benchmark.env"
APPLICATION_SETTINGS_FILE_PATH = Path("settings") / "application.env"
ANALYZE_SETTINGS_FILE_PATH = Path("settings") / "analyze.env"
ENGINE_SETTINGS_FILE_PATH = Path("settings") / "engine.env"


class EngineSettings(BaseSettings):
    ANALYSE_DEPTH: int
    MOVE_ACCEPTANCE_THRESHOLD_CENTI_PAWS: int
    MULTI_PV: int

    model_config = SettingsConfigDict(
        env_file=ENGINE_SETTINGS_FILE_PATH, env_file_encoding="utf-8", case_sensitive=True, frozen=False
    )


class BenchmarkSettings(BaseSettings):
    BENCHMARKING_MODEL: str
    EXTRACTION_MODEL: Optional[str]

    MAX_MOVES: int
    MAX_ILLEGAL_MOVES: int

    STRATEGY: Optional[str] = None

    engine_settings: dict[str, int] = {}

    model_extra_config: dict[str, Any] = {}

    @model_validator(mode="after")
    def check_extraction_strategy(self):
        if self.STRATEGY == "move_and_extract" and self.EXTRACTION_MODEL is None:
            raise ValueError("EXTRACTION_MODEL can not be null in move_and_extract strategy!")
        return self

    model_config = SettingsConfigDict(
        env_file=BENCHMARK_SETTINGS_FILE_PATH, env_file_encoding="utf-8", case_sensitive=True, frozen=False
    )


class ApplicationSettings(BaseSettings):
    ENVIRONMENT: Environment
    LOGGING_LEVEL: Optional[str] = None

    PLAYS_NUMBER: int
    MAX_WORKERS: int

    COLOR_GENERATOR: ColorGenerator

    APPEND_RESULTS: bool

    RETRY_NUMBER: int
    MINIMUM_WAIT_SECONDS: int
    MAXIMUM_WAIT_SECONDS: int

    model_config = SettingsConfigDict(
        env_file=APPLICATION_SETTINGS_FILE_PATH, env_file_encoding="utf-8", case_sensitive=True, frozen=True
    )


class AnalyzeSettings(BaseSettings):
    DEBUT_OFFSET: int

    model_config = SettingsConfigDict(
        env_file=ANALYZE_SETTINGS_FILE_PATH, env_file_encoding="utf-8", case_sensitive=True, frozen=True
    )


class Settings(BaseSettings):
    benchmark: BenchmarkSettings = BenchmarkSettings()
    application: ApplicationSettings = ApplicationSettings()
    analyze: AnalyzeSettings = AnalyzeSettings()
    engine: EngineSettings = EngineSettings()

    model_config = SettingsConfigDict(case_sensitive=True, frozen=True)


settings = Settings()
