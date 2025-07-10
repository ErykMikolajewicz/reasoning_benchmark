from enum import Enum

class GameResult(float, Enum):
    WIN = 1.
    TIE = 0.5
    LOSS = 0.
    LOSS_INVALID_MOVE = float('nan')