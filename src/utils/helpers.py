import hashlib
import json
from itertools import cycle
import random
from typing import Generator

from chess import Board, Color, BLACK, WHITE, COLORS

import src.chess_logic.prompts as prompts
from src.share.conts import COLORS_STRING_DICT, MODELS_SHORT_NAME
from src.share.enums import ColorGenerator


def hash_dict(dict_) -> str:
    dict_str = json.dumps(dict_, sort_keys=True)
    hash_obj = hashlib.sha256(dict_str.encode("utf-8"))
    hash_str = hash_obj.hexdigest()
    return hash_str


def get_model_shorter_name(name: str) -> str:
    try:
        short_name = MODELS_SHORT_NAME[name]
        return short_name
    except KeyError:
        return name


def format_board_info(board: Board, llm_color: Color, last_opponent_move: str) -> str:
    llm_color = COLORS_STRING_DICT[llm_color]
    castling_rights = board.castling_xfen()
    ascii_board = str(board)
    full_board_info = prompts.board_prompt.format(
        ascii_board=ascii_board,
        castling_rights=castling_rights,
        last_opponent_move=last_opponent_move,
        llm_color=llm_color,
    )

    return full_board_info


def get_color_generator(generator_name: str) -> Generator[Color, None, None]:
    match generator_name:
        case ColorGenerator.WHITE:
            color_generator = cycle((WHITE,))
        case ColorGenerator.BLACK:
            color_generator = cycle((BLACK,))
        case ColorGenerator.BOTH:
            color_generator = cycle(COLORS)
        case ColorGenerator.RANDOM:
            def color_generator():
                while True:
                    yield random.choice(COLORS)
        case _:
            raise NotImplementedError

    return color_generator
