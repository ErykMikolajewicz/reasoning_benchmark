from pydantic_settings import BaseSettings, SettingsConfigDict


class EngineSettings(BaseSettings):
    ANALYSE_DEPTH: int = ...
    MOVE_ACCEPTANCE_THRESHOLD_CENTI_PAWS: int = ...
    MULTI_PV: int = ...

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="ENGINE_",
        case_sensitive=True,
        frozen=False,
        extra="ignore",
    )


engine_settings = EngineSettings()
