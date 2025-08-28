from enum import StrEnum


class GameResult(StrEnum):
    WIN = "WIN"
    TIE = "TIE"
    LOSS = "LOSS"
    LOSS_INVALID_MOVE = "LOSS_INVALID_MOVE"
    MAX_MOVES = "MAX_MOVES"


class ColorGenerator(StrEnum):
    WHITE = "WHITE"
    BLACK = "BLACK"
    BOTH = "BOTH"
    RANDOM = "RANDOM"


class Environment(StrEnum):
    LOCAL = "LOCAL"
    GOOGLE_CLOUD = "GOOGLE_CLOUD"
