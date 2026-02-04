import random

import chess.engine
from chess import Color

from domain.types import LlmStrategy
from domain.utils.helpers import format_board_info
from infrastructure.models_adapter import LLMAdapter


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

    def get_move(self, board) -> str:
        moves = self.__engine.analyse(board, self._analyze_limit, multipv=self._multi_pv)
        acceptable_moves = self._choose_acceptable_moves(moves)
        move = random.choice(acceptable_moves)
        move = move["pv"][0]
        move = board.san(move)
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
    def __init__(self, llm_strategy: LlmStrategy, llm_color: Color):
        self._llm_color = llm_color
        self._llm_adapter = LLMAdapter()
        self._llm_strategy = llm_strategy
        self._game_data = {}

    def get_move(self, board, last_opponent_move):
        board_info = format_board_info(board, self._llm_color, last_opponent_move)
        move = self._llm_strategy(self._llm_adapter, board_info, self._game_data)
        return move
