import hashlib
import json

from chess import Board, Color

from src.domain.value_objects.board import BoardInfo
from src.share.conts import COLORS_STRING_DICT


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
