import logging
import random

import chess.engine
from chess import Color, Move

from domain.exceptions import InvalidMove
from domain.types import LlmStrategy
from domain.utils.helpers import format_board_info
from infrastructure.models_adapter import LLMAdapter

logger = logging.getLogger(__name__)


class EngineMover:
    def __init__(self, color: Color, analyse_depth: int, multi_pv: int, acceptance_threshold: int):
        self._engine = None
        self._color = color
        self._analyze_limit = chess.engine.Limit(depth=analyse_depth)
        self._multi_pv = multi_pv
        self._acceptance_threshold = acceptance_threshold

    def __enter__(self):
        self.__engine = chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__engine.quit()
        self.__engine = None

    def make_move(self, board) -> str:
        moves = self.__engine.analyse(board, self._analyze_limit, multipv=self._multi_pv)
        acceptable_moves = self._choose_acceptable_moves(moves)
        move = random.choice(acceptable_moves)
        move = move["pv"][0]
        move = board.san(move)
        board.push_san(move)
        return move

    def _choose_acceptable_moves(self, engine_moves: list[chess.engine.InfoDict]) -> list[chess.engine.InfoDict]:
        moves_engine_view = [move["score"].pov(self._color) for move in engine_moves]
        max_score = max([score for move in moves_engine_view if (score := move.score()) is not None])
        acceptable_moves = []
        for move, move_engine_view in zip(engine_moves, moves_engine_view, strict=True):
            score = move_engine_view.score()
            if score is None:
                acceptable_moves.append(move)
            else:
                if score > max_score - self._acceptance_threshold:
                    acceptable_moves.append(move)
        return acceptable_moves


class LlmMover:
    def __init__(self, llm_strategy: LlmStrategy, llm_color: Color, max_illegal_moves: int):
        self._llm_color = llm_color
        self._llm_adapter = LLMAdapter()
        self._llm_strategy = llm_strategy
        self._illegal_moves = 0
        self._max_illegal_moves = max_illegal_moves
        self._game_data = {}

    def make_move(self, board) -> str:
        try:
            previous_move: Move = board.peek()
        except IndexError:
            previous_move_str = "None"
        else:
            previous_move_str = previous_move.uci()
        board_info = format_board_info(board, self._llm_color, previous_move_str)

        while True:
            move = self._llm_strategy(self._llm_adapter, board_info, self._game_data)
            try:
                board.push_san(move)
            except ValueError as e:
                self._illegal_moves += 1
                logger.warning(f"Illegal move, number: {self._illegal_moves}")
                if self._illegal_moves < self._max_illegal_moves:
                    logger.warning("Illegal moves, number exceeded!")
                    raise InvalidMove(move) from e
            else:
                return move
