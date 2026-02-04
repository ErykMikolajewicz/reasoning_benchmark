from chess import Color

import domain.llm.strategies as strategies
import domain.types
from domain.llm.enums import LlmStrategy
from domain.services.moves import LlmMover
from share.settings.benchmark import benchmark_settings


def get_llm_strategy() -> domain.types.LlmStrategy:
    match benchmark_settings.STRATEGY:
        case LlmStrategy.MAINTAIN_STRATEGY:
            return strategies.maintain_strategy
        case LlmStrategy.SIMPLE_MOVE:
            return strategies.simple_move
        case LlmStrategy.DEFAULT:
            return strategies.simple_move
        case LlmStrategy.HUMAN_PLAY:
            return strategies.human_play
        case _:
            raise Exception("Invalid config, bad llm strategy")


def get_llm_mover(llm_color: Color) -> LlmMover:
    llm_strategy = get_llm_strategy()
    return LlmMover(llm_strategy, llm_color)
