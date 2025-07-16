from pathlib import Path
from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BENCHMARK_SETTINGS_FILE_PATH = Path('settings') / 'benchmark.env'
APPLICATION_SETTINGS_FILE_PATH = Path('settings') / 'application.env'


class BenchmarkSettings(BaseSettings):
    MAX_MOVES: int

    BENCHMARKING_MODEL: str
    EXTRACTION_MODEL: Optional[str]

    STRATEGY: Optional[str] = None

    DEBUT_OFFSET: int

    MAX_ILLEGAL_MOVES: int

    @model_validator(mode='after')
    def check_extraction_strategy(self):
        if self.STRATEGY == 'move_and_extract' and self.EXTRACTION_MODEL is None:
            raise ValueError("EXTRACTION_MODEL can not be null in move_and_extract strategy!")
        return self

    model_config = SettingsConfigDict(
        env_file=BENCHMARK_SETTINGS_FILE_PATH, env_file_encoding="utf-8", case_sensitive=True, frozen=True
    )


class ApplicationSettings(BaseSettings):
    LOGGING_LEVEL: Optional[str] = None

    PLAYS_NUMBER: int
    MAX_WORKERS: int

    APPEND_RESULTS: bool

    RETRY_NUMBER: int
    MINIMUM_WAIT_SECONDS: int
    MAXIMUM_WAIT_SECONDS: int

    model_config = SettingsConfigDict(
        env_file=APPLICATION_SETTINGS_FILE_PATH, env_file_encoding="utf-8", case_sensitive=True, frozen=True
    )


class Settings(BaseSettings):
    benchmark: BenchmarkSettings = BenchmarkSettings()
    application: ApplicationSettings = ApplicationSettings()

    model_config = SettingsConfigDict(case_sensitive=True, frozen=True)


settings = Settings()
