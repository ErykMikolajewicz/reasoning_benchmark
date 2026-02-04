from dataclasses import dataclass


@dataclass
class BoardInfo:
    ascii_board: str
    castling_rights: str
    last_opponent_move: str
    llm_color: str
