from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class BenchmarkSettings(BaseSettings):
    MODEL: str = ...

    MAX_PLY: int = ...
    MAX_ILLEGAL_MOVES: int = ...

    STRATEGY: str | None = None

    engine_settings: dict[str, int] = {}

    model_extra_config: dict[str, Any] = {}

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="BENCHMARK_",
        case_sensitive=True,
        frozen=False,
        extra="ignore",
    )


benchmark_settings = BenchmarkSettings()
