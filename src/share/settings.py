from pathlib import Path
from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.share.enums import ColorGenerator

BENCHMARK_SETTINGS_FILE_PATH = Path("settings") / "benchmark.env"
APPLICATION_SETTINGS_FILE_PATH = Path("settings") / "application.env"
ANALYZE_SETTINGS_FILE_PATH = Path("settings") / "analyze.env"


class BenchmarkSettings(BaseSettings):
    MAX_MOVES: int

    BENCHMARKING_MODEL: str
    EXTRACTION_MODEL: Optional[str]

    STRATEGY: Optional[str] = None

    MAX_ILLEGAL_MOVES: int

    MODEL_EXTRA_CONFIG: dict = {}

    @model_validator(mode="after")
    def check_extraction_strategy(self):
        if self.STRATEGY == "move_and_extract" and self.EXTRACTION_MODEL is None:
            raise ValueError("EXTRACTION_MODEL can not be null in move_and_extract strategy!")
        return self

    model_config = SettingsConfigDict(
        env_file=BENCHMARK_SETTINGS_FILE_PATH, env_file_encoding="utf-8", case_sensitive=True, frozen=False
    )


class ApplicationSettings(BaseSettings):
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

    model_config = SettingsConfigDict(case_sensitive=True, frozen=True)


settings = Settings()
