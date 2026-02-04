import hashlib
import json
import random
from itertools import cycle
from typing import Generator

from chess import BLACK, COLORS, WHITE, Board, Color

from src.share.conts import COLORS_STRING_DICT
from src.share.enums import ColorGenerator
from src.domain.schemas import BoardInfo


def hash_dict(dict_) -> str:
    dict_str = json.dumps(dict_, sort_keys=True)
    hash_obj = hashlib.sha256(dict_str.encode("utf-8"))
    hash_str = hash_obj.hexdigest()
    return hash_str


def format_board_info(board: Board, llm_color: Color, last_opponent_move: str) -> BoardInfo:
    llm_color = COLORS_STRING_DICT[llm_color]
    castling_rights = board.castling_xfen()
    ascii_board = str(board)
    board_info = BoardInfo(
        ascii_board=ascii_board,
        castling_rights=castling_rights,
        last_opponent_move=last_opponent_move,
        llm_color=llm_color,
    )

    return board_info


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
