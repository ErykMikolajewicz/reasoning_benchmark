from dataclasses import dataclass

from domain.llm.enums import LlmStrategy


@dataclass
class EngineSettings:
    analyse_depth: int
    acceptance_threshold: int
    multi_pv: int


@dataclass(frozen=True)
class BenchmarkConfig:
    model: str
    strategy: LlmStrategy
    max_ply: int
    max_illegal_moves: int
    engine_settings: EngineSettings
    model_extra_config: dict
