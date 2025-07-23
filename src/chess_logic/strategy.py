import json
from typing import Dict, Optional

import src.chess_logic.prompts as prompts
from src.share.custom_types import GameStrategy
from src.share.settings import settings
from src.utils.models_adapter import LLMAdapter

BENCHMARKING_MODEL = settings.benchmark.BENCHMARKING_MODEL
EXTRACTION_MODEL = settings.benchmark.EXTRACTION_MODEL


def simple_move(llm_adapter: LLMAdapter, board_info: str) -> str:
    move_and_thinking = llm_adapter.send_messages(
        model=BENCHMARKING_MODEL,
        messages=[{"role": "system", "content": prompts.move_formated}, {"role": "user", "content": board_info}],
    )

    json_start_index = move_and_thinking.index("{")
    json_end_index = move_and_thinking.rindex("}")
    only_move = move_and_thinking[json_start_index : json_end_index + 1]
    move_json = json.loads(only_move)
    move = move_json["move"]

    return move


def move_and_extract(llm_adapter: LLMAdapter, board_info: str) -> str:
    response = llm_adapter.send_messages(
        model=BENCHMARKING_MODEL,
        messages=[{"role": "system", "content": prompts.move_prompt}, {"role": "user", "content": board_info}],
    )

    move_and_thinking: str = response

    response = llm_adapter.send_messages(
        model=EXTRACTION_MODEL,
        messages=[
            {"role": "system", "content": prompts.EXTRACTION_PROMPT},
            {"role": "user", "content": move_and_thinking},
        ],
    )

    move_str: str = response
    json_start_index = move_str.index("{")
    json_end_index = move_str.rindex("}")
    move_json = json.loads(move_str[json_start_index : json_end_index + 1])
    move = move_json["move"]

    return move


strategies: Dict[Optional[str], GameStrategy] = {
    None: simple_move,
    "simple_move": simple_move,
    "move_and_extract": move_and_extract,
}
