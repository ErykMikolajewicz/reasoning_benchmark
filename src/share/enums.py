from enum import Enum, auto


class GameResult(str, Enum):
    WIN = "WIN"
    TIE = "TIE"
    LOSS = "LOSS"
    LOSS_INVALID_MOVE = "LOSS_INVALID_MOVE"
    MAX_MOVES = "MAX_MOVES"
