from typing import Dict, Optional
import logging

import src.chess_logic.prompts as prompts
from src.share.custom_types import GameStrategy
from src.share.settings import settings
from src.utils.models_adapter import LLMAdapter
from src.utils.helpers import extract_json
from src.share.exceptions import NoJsonInText

BENCHMARKING_MODEL = settings.benchmark.BENCHMARKING_MODEL
EXTRACTION_MODEL = settings.benchmark.EXTRACTION_MODEL

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


def move_and_extract(llm_adapter: LLMAdapter, board_info: str, _: dict) -> str:
    move_and_thinking = llm_adapter.send_messages(
        model=BENCHMARKING_MODEL,
        messages=[{"role": "system", "content": prompts.move_prompt}, {"role": "user", "content": board_info}],
    )

    move_str = llm_adapter.send_messages(
        model=EXTRACTION_MODEL,
        messages=[
            {"role": "system", "content": prompts.EXTRACTION_PROMPT},
            {"role": "user", "content": move_and_thinking},
        ],
    )

    try:
        move_json = extract_json(move_and_thinking)
    except NoJsonInText:
        return f"Invalid move format: {move_str}"

    move = move_json["move"]

    return move


def human_play(_: LLMAdapter, board_info: str, _2: dict):
    print(board_info)
    move = input("Write move in SAN notation: ")
    return move


def maintain_strategy(llm_adapter: LLMAdapter, board_info: str, game_state: dict) -> str:
    strategy = game_state.get("strategy")

    board_and_strategy = (
        board_info + f"""\nYour strategy:
        {strategy}"""
    )

    move_with_strategy = llm_adapter.send_messages(
        model=BENCHMARKING_MODEL,
        messages=[{"role": "system", "content": prompts.move_with_strategy},
                  {"role": "user", "content": board_and_strategy}],
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


strategies: Dict[Optional[str], GameStrategy] = {
    None: simple_move,
    "simple_move": simple_move,
    "move_and_extract": move_and_extract,
    "human_play": human_play,
    "maintain_strategy": maintain_strategy
}
