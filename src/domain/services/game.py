import logging

from chess import WHITE, Board, Color

from dependencies.engine import get_engine_mover
from dependencies.llm import get_llm_mover
from domain.enums import GameResult
from domain.exceptions import InvalidMove
from domain.services.moves import EngineMover, LlmMover
from domain.value_objects.pydantic_models import GameData
from share.settings.benchmark import benchmark_settings

MAX_ILLEGAL_MOVES = benchmark_settings.MAX_ILLEGAL_MOVES
MAX_PLY = benchmark_settings.MAX_PLY

logger = logging.getLogger(__name__)


class Game:
    def __init__(self, llm_mover: LlmMover, llm_color: Color, engine_mover: EngineMover):
        self._board = Board()
        self.moves_history = []
        self._current_ply = 1
        self._illegal_moves = 0
        self._whose_turn = WHITE
        self._match_result = None
        self._engine_mover = engine_mover
        self._llm_mover = llm_mover
        self._llm_color = llm_color

    def play(self) -> GameResult:
        with self._engine_mover:
            while self._current_ply <= MAX_PLY and not self._board.is_game_over():
                try:
                    self._make_move(self._llm_color)
                except InvalidMove as e:
                    self._illegal_moves += 1
                    logger.warning(f"Illegal move, number: {self._illegal_moves}")
                    if self._illegal_moves < MAX_ILLEGAL_MOVES:
                        continue
                    else:
                        invalid_move = e.invalid_move
                        self.moves_history.append(invalid_move)
                        logger.warning("Illegal moves, number exceeded!")
                        self._match_result = GameResult.LOSS_INVALID_MOVE
                        raise RuntimeError("To many invalid moves") from None

                self._current_ply += 1
                self._whose_turn = not self._whose_turn

        match self._board.result(), self._llm_color:
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
                match_result = GameResult.DRAW

        self._match_result = match_result

        return match_result

    def _make_move(self, llm_color: Color):
        logger.info(f"Ply number: {self._current_ply}")
        if self._whose_turn == llm_color:
            try:
                last_opponent_move = self.moves_history[-1]
            except IndexError:
                last_opponent_move = "None"
            move = self._llm_mover.get_move(self._board, last_opponent_move)
            logger.info(f"LLM ply: {move}")
            try:
                self._board.push_san(move)
            except ValueError as e:
                raise InvalidMove(invalid_move=move) from e
        else:
            move = self._engine_mover.get_move(self._board)
            logger.info(f"Engine ply: {move}")
            self._board.push_san(move)
        self.moves_history.append(move)


def run_game(llm_color: Color) -> GameData:
    llm_mover = get_llm_mover(llm_color)

    engine_color = not llm_color
    engine_mover = get_engine_mover(engine_color)

    game = Game(llm_mover, llm_color, engine_mover)
    try:
        game_result = game.play()
    except RuntimeError:
        game_result = GameResult.LOSS_INVALID_MOVE
    game_history = game.moves_history

    game_data = GameData(result=game_result, history=game_history, llm_color=llm_color)
    return game_data
