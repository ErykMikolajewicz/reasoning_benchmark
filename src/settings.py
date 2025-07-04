from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

BENCHMARK_SETTINGS_FILE_PATH = Path("settings") / 'benchmark.env'


class BenchmarkSettings(BaseSettings):
    MAX_MOVES: int
    PLAYS_NUMBER: int

    BENCHMARKING_MODEL: str
    EXTRACTION_MODEL: str

    STRATEGY: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=BENCHMARK_SETTINGS_FILE_PATH, env_file_encoding="utf-8", case_sensitive=True, frozen=True
    )


class Settings(BaseSettings):
    benchmark: BenchmarkSettings = BenchmarkSettings()

    model_config = SettingsConfigDict(case_sensitive=True, frozen=True)


settings = Settings()
