from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

BENCHMARK_SETTINGS_FILE_PATH = Path('settings') / 'benchmark.env'
APPLICATION_SETTINGS_FILE_PATH = Path('settings') / 'application.env'


class BenchmarkSettings(BaseSettings):
    MAX_MOVES: int
    MAX_ILLEGAL_MOVES: int
    PLAYS_NUMBER: int

    STRATEGY: Optional[str] = None

    BENCHMARKING_MODEL: str
    EXTRACTION_MODEL: str

    DEBUT_OFFSET: int

    model_config = SettingsConfigDict(
        env_file=BENCHMARK_SETTINGS_FILE_PATH, env_file_encoding="utf-8", case_sensitive=True, frozen=True
    )

class ApplicationSettings(BaseSettings):
    LOGGING_LEVEL: Optional[str] = None
    MAX_WORKERS: int

    model_config = SettingsConfigDict(
        env_file=APPLICATION_SETTINGS_FILE_PATH, env_file_encoding="utf-8", case_sensitive=True, frozen=True
    )


class Settings(BaseSettings):
    benchmark: BenchmarkSettings = BenchmarkSettings()
    application: ApplicationSettings = ApplicationSettings()

    model_config = SettingsConfigDict(case_sensitive=True, frozen=True)


settings = Settings()
