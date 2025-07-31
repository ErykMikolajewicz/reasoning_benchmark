import logging
from typing import Optional
import random

import chess.engine
from chess import WHITE, Board, Color

from src.chess_logic.strategy import strategies
from src.models import GameData
from src.share.custom_types import GameStrategy
from src.share.enums import GameResult
from src.share.exceptions import InvalidMove
from src.share.settings import settings
from src.utils.helpers import format_board_info
from src.utils.models_adapter import LLMAdapter
from src.share.conts import ENGINE_MULTI_PV, ENGINE_CENTI_PAWS_THRESHOLD, ENGINE_DEPTH

MAX_MOVES = settings.benchmark.MAX_MOVES
MAX_ILLEGAL_MOVES = settings.benchmark.MAX_ILLEGAL_MOVES

logger = logging.getLogger(__name__)


class Game:
    def __init__(self, llm_strategy: GameStrategy):
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
            try:
                last_opponent_move = self.moves_history[-1]
            except IndexError:
                last_opponent_move = "None"
            board_info = format_board_info(self._board, llm_color, last_opponent_move)
            move = self._llm_strategy(self._llm_adapter, board_info)
            logger.info(f"LLM move: {move}")
            try:
                self._board.push_san(move)
            except ValueError:
                raise InvalidMove(invalid_move=move)
        else:
            moves = self.__engine.analyse(self._board, chess.engine.Limit(depth=ENGINE_DEPTH), multipv=ENGINE_MULTI_PV)
            acceptable_moves = self._choose_acceptable_moves(moves)
            move = random.choice(acceptable_moves)
            move = move['pv'][0]
            move = self._board.san(move)
            logger.info(f"Engine move: {move}")
            self._board.push_san(move)
        self.moves_history.append(move)

    def _choose_acceptable_moves(self, engine_moves: list[chess.engine.InfoDict]) -> list[chess.engine.InfoDict]:
        moves_engine_view = [move['score'].pov(self._whose_turn) for move in engine_moves]
        max_score = max([score for move in moves_engine_view if (score := move.score()) is not None])
        acceptable_moves = []
        for move, move_engine_view in zip(engine_moves, moves_engine_view):
            score = move_engine_view.score()
            if score is None:
                acceptable_moves.append(move)
            else:
                if score > max_score - ENGINE_CENTI_PAWS_THRESHOLD:
                    acceptable_moves.append(move)
        return acceptable_moves


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
