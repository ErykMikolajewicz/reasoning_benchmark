import hashlib
import json

from chess import Board, Color

import src.chess_logic.prompts as prompts
from src.share.conts import COLORS_STRING_DICT, MODELS_SHORT_NAME


def hash_dict(dict_) -> str:
    dict_str = json.dumps(dict_, sort_keys=True)
    hash_obj = hashlib.sha256(dict_str.encode("utf-8"))
    hash_str = hash_obj.hexdigest()
    return hash_str


def get_model_shorter_name(name: str):
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
