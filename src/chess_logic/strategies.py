import logging
from typing import Dict, Optional

import src.chess_logic.prompts as prompts
from src.settings import settings
from src.share.custom_types import GameStrategy
from src.share.exceptions import NoJsonInText
from src.utils.helpers import extract_json
from src.utils.models_adapter import LLMAdapter

BENCHMARKING_MODEL = settings.benchmark.BENCHMARKING_MODEL

logger = logging.getLogger(__name__)


def simple_move(llm_adapter: LLMAdapter, board_info: str, _: dict) -> str:
    move_and_thinking = llm_adapter.send_messages(
        model=BENCHMARKING_MODEL,
        messages=[{"role": "system", "content": prompts.move_formated}, {"role": "user", "content": board_info}],
    )

    try:
        move_json = extract_json(move_and_thinking)
    except NoJsonInText:
        return f"Invalid move format: {move_and_thinking}"

    move = move_json["move"]

    return move


def human_play(_: LLMAdapter, board_info: str, _2: dict):
    print(board_info)
    move = input("Write move in SAN notation: ")
    return move


def maintain_strategy(llm_adapter: LLMAdapter, board_info: str, game_state: dict) -> str:
    strategy = game_state.get("strategy")

    board_and_strategy = board_info + f"\nYour strategy:\n{strategy}"

    move_with_strategy = llm_adapter.send_messages(
        model=BENCHMARKING_MODEL,
        messages=[
            {"role": "system", "content": prompts.move_with_strategy},
            {"role": "user", "content": board_and_strategy},
        ],
    )

    try:
        move_with_strategy = extract_json(move_with_strategy)
    except NoJsonInText:
        return f"Invalid move format: {move_with_strategy}"

    move = move_with_strategy["move"]

    strategy = move_with_strategy["strategy"]
    game_state["strategy"] = strategy

    logger.info(f"LLM strategy: {strategy}")

    return move


aviable_strategies: Dict[Optional[str], GameStrategy] = {
    None: simple_move,
    "simple_move": simple_move,
    "human_play": human_play,
    "maintain_strategy": maintain_strategy,
}
