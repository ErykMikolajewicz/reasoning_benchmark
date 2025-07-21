import logging
from typing import Callable, Optional

import chess.engine
from chess import WHITE, Board, Color

from src.chess_logic.strategy import strategies
from src.models import GameData
from src.share.enums import GameResult
from src.share.exceptions import InvalidMove
from src.share.settings import settings
from src.utils.models_adapter import LLMAdapter

MAX_MOVES = settings.benchmark.MAX_MOVES
MAX_ILLEGAL_MOVES = settings.benchmark.MAX_ILLEGAL_MOVES

logger = logging.getLogger(__name__)


class Game:
    def __init__(self, llm_strategy: Callable[[LLMAdapter, Board, Color], str]):
        self._board = Board()
        self.moves_history = []
        self._current_move = 1
        self._illegal_moves = 0
        self._whose_turn = WHITE
        self._engine = None
        self._llm_adapter = LLMAdapter()
        self._llm_strategy = llm_strategy
        self._is_game_ended = False
        self._match_result = None

    def __enter__(self):
        self.__engine = chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__engine.quit()
        self.__engine = None

    def play(self, llm_color: Color) -> GameResult:
        while self._current_move <= MAX_MOVES and not self._board.is_game_over():
            try:
                self._make_move(llm_color)
            except InvalidMove as e:
                self._illegal_moves += 1
                logger.warning(f"Illegal move, number: {self._illegal_moves}")
                if self._illegal_moves < MAX_ILLEGAL_MOVES:
                    continue
                else:
                    invalid_move = e.invalid_move
                    self.moves_history.append(invalid_move)
                    logger.warning(f"Illegal moves, number exceeded!")
                    self._is_game_ended = True
                    self._match_result = GameResult.LOSS_INVALID_MOVE
                    raise RuntimeError("To many invalid moves")

            self._current_move += 1
            self._whose_turn = not self._whose_turn

        self._is_game_ended = True

        match self._board.result(), llm_color:
            case "*", _:
                match_result = GameResult.MAX_MOVES
            case "1-0", True:
                match_result = GameResult.WIN
            case "1-0", False:
                match_result = GameResult.LOSS
            case "0-1", True:
                match_result = GameResult.LOSS
            case "0-1", False:
                match_result = GameResult.WIN
            case _:
                match_result = GameResult.TIE

        self._match_result = match_result

        return match_result

    def _make_move(self, llm_color: Color):
        logger.info(f"Move number: {self._current_move}")
        if self._whose_turn == llm_color:
            move = self._llm_strategy(self._llm_adapter, self._board, llm_color)
            logger.info(f"LLM move: {move}")
            try:
                self._board.push_san(move)
            except ValueError:
                raise InvalidMove(invalid_move=move)
        else:
            result = self.__engine.play(self._board, chess.engine.Limit(depth=1, time=0.0005))
            move = result.move
            logger.info(f"Engine move: {move}")
            self._board.push(move)
        self.moves_history.append(str(move))


def run_game(llm_color: Color, llm_strategy: Optional[str] = None) -> GameData:
    try:
        selected_strategy = strategies[llm_strategy]
    except KeyError:
        raise ValueError("Invalid strategy!")
    game = Game(selected_strategy)
    with game:
        try:
            game_result = game.play(llm_color=llm_color)
        except RuntimeError:
            game_result = GameResult.LOSS_INVALID_MOVE
    game_history = game.moves_history

    game_data = GameData(result=game_result, history=game_history, llm_color=llm_color)
    return game_data
