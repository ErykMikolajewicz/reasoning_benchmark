import json
import logging

from jinja2 import Environment, StrictUndefined

import domain.llm.prompts as prompts
import domain.llm.responses as llm_resp
from domain.value_objects.board import BoardInfo
from infrastructure.models_adapter import LLMAdapter

logger = logging.getLogger(__name__)


def simple_move(llm_adapter: LLMAdapter, board_info: BoardInfo, _: dict) -> str:
    env = Environment(
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    template = env.from_string(prompts.simple_move)

    data = {
        "ascii_board": board_info.ascii_board,
        "castling_rights": board_info.castling_rights,
        "last_opponent_move": board_info.last_opponent_move,
        "llm_color": board_info.llm_color,
    }

    prompt = template.render(**data)

    move = llm_adapter.send_messages(
        messages=[
            {"role": "user", "content": prompt},
        ],
        response_format=llm_resp.move,
    )

    move = json.loads(move)

    move = move["move"]

    return move


def human_play(_: LLMAdapter, board_info: BoardInfo, _2: dict) -> str:
    print(board_info)
    move = input("Write move in SAN notation: ")
    return move


def maintain_strategy(llm_adapter: LLMAdapter, board_info: BoardInfo, game_state: dict) -> str:
    strategy = game_state.get("strategy")

    env = Environment(
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    template = env.from_string(prompts.maintain_strategy)

    data = {
        "ascii_board": board_info.ascii_board,
        "castling_rights": board_info.castling_rights,
        "last_opponent_move": board_info.last_opponent_move,
        "llm_color": board_info.llm_color,
        "strategy": strategy,
    }

    prompt = template.render(**data)

    move_with_strategy = llm_adapter.send_messages(
        messages=[
            {"role": "user", "content": prompt},
        ],
        response_format=llm_resp.strategy,
    )

    move_with_strategy = json.loads(move_with_strategy)

    move = move_with_strategy["move"]

    strategy = move_with_strategy["strategy"]
    game_state["strategy"] = strategy

    logger.info(f"LLM strategy: {strategy}")

    return move
