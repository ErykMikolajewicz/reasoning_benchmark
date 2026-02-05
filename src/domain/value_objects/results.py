from dataclasses import dataclass
from decimal import Decimal

from domain.value_objects.benchmark import BenchmarkConfig
from domain.value_objects.game import GameData


@dataclass
class ModelUsage:
    prompt_tokens: int = 0
    reasoning_tokens: int = 0
    text_tokens: int = 0
    total_cost_dollar: Decimal = Decimal(0.0)

    def __add__(self, other: "ModelUsage") -> "ModelUsage":
        if not isinstance(other, ModelUsage):
            return NotImplemented
        return ModelUsage(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            reasoning_tokens=self.reasoning_tokens + other.reasoning_tokens,
            text_tokens=self.text_tokens + other.text_tokens,
            total_cost_dollar=self.total_cost_dollar + other.total_cost_dollar,
        )


@dataclass
class BenchmarkingResult:
    benchmark_config: BenchmarkConfig
    usage: ModelUsage
    games_data: list[GameData]
