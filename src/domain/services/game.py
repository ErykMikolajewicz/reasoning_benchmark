import logging

import chess

from domain.enums import GameResult
from domain.exceptions import InvalidMove
from domain.services.moves import EngineMover, LlmMover

logger = logging.getLogger(__name__)


class Game:
    def __init__(self, llm_mover: LlmMover, llm_color: chess.Color, engine_mover: EngineMover, max_ply: int):
        self._board = chess.Board()
        self._moves_history = []
        self._current_ply = 0
        self._engine_mover = engine_mover
        self._llm_mover = llm_mover
        self._llm_color = llm_color
        self._max_ply = max_ply

    def play(self) -> tuple[GameResult, list[str]]:

        try:
            with self._engine_mover:
                self._launch_moves_loop()
        except InvalidMove as e:
            move = e.invalid_move
            self._moves_history.append(move)
            game_result = GameResult.LOSS_INVALID_MOVE
        else:
            game_result = self._evaluate_board()

        return game_result, self._moves_history

    def _launch_moves_loop(self):
        while self._current_ply < self._max_ply and not self._board.is_game_over():
            self._current_ply += 1
            logger.info(f"Ply number: {self._current_ply}")

            if self._board.turn == self._llm_color:
                move = self._llm_mover.make_move(self._board)
                logger.info(f"LLM ply: {move}")
            else:
                move = self._engine_mover.make_move(self._board)
                logger.info(f"Engine ply: {move}")
            self._moves_history.append(move)

    def _evaluate_board(self):
        match self._board.result():
            case "*":
                match_result = GameResult.MAX_MOVES
            case "1-0":
                if self._llm_color == chess.WHITE:
                    match_result = GameResult.WIN
                else:
                    match_result = GameResult.LOSS
            case "0-1":
                if self._llm_color == chess.BLACK:
                    match_result = GameResult.WIN
                else:
                    match_result = GameResult.LOSS
            case _:
                match_result = GameResult.DRAW

        return match_result
