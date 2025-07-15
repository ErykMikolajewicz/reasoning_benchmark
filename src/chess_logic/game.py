from typing import Callable, Optional
from statistics import mean
import logging
from itertools import repeat, islice, chain

import chess.engine
from chess import Board, WHITE, Color

from src.chess_logic.strategy import strategies
from src.utils.models_adapter import LLMAdapter
from src.share.settings import settings
from src.share.enums import GameResult
from src.share.conts import MAX_POSITION_SCORE, MIN_POSITION_SCORE, TIE_SCORE

MAX_MOVES = settings.benchmark.MAX_MOVES
MAX_ILLEGAL_MOVES = settings.benchmark.MAX_ILLEGAL_MOVES
DEBUT_OFFSET = settings.benchmark.DEBUT_OFFSET

logger = logging.getLogger(__name__)


class Game:
    def __init__(self, llm_strategy: Callable[[LLMAdapter, Board, Color], str]):
        self._board = Board()
        self._current_move = 1
        self._illegal_moves = 0
        self._whose_turn = WHITE
        self.position_scores: list[float] = []
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

    def play(self, llm_color: Color):
        while self._current_move <= MAX_MOVES and not self._board.is_game_over():
            try:
                self._make_move(llm_color)
            except ValueError:
                self._illegal_moves += 1
                logger.warning(f'Illegal move, number: {self._illegal_moves}')
                if self._illegal_moves < MAX_ILLEGAL_MOVES:
                    continue
                else:
                    logger.warning(f'Illegal moves, number exceeded!')
                    self._is_game_ended = True
                    self._match_result = GameResult.LOSS_INVALID_MOVE
                    raise RuntimeError('To many invalid moves')

            self._current_move += 1
            self._score_position(llm_color)
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

        return match_result, self.position_scores

    def get_game_score(self) -> float:
        if not self._is_game_ended:
            logger.error('Try get game score to early!')
            raise RuntimeError('Game not ended!')

        try:
            relevant_scores = self.position_scores[DEBUT_OFFSET:]
        except IndexError:
            relevant_scores = []

        after_debut_moves = MAX_MOVES - DEBUT_OFFSET

        match self._match_result:
            case GameResult.WIN:
                padding_source = repeat(MAX_POSITION_SCORE)
            case GameResult.TIE:
                padding_source = repeat(TIE_SCORE)
            case GameResult.LOSS:
                padding_source = repeat(MIN_POSITION_SCORE)
            case GameResult.LOSS_INVALID_MOVE:
                padding_source = repeat(MIN_POSITION_SCORE)
            case GameResult.MAX_MOVES:
                # Party is not ended, and moves should not require padding
                class PaddingGuard:
                    def __iter__(self):
                        return self

                    def __next__(self):
                        raise RuntimeError("Unexpected padding score requested!")
                padding_source = PaddingGuard()
            case _:
                raise RuntimeError('Invalid game result status!')

        scores_with_padding = islice(chain(relevant_scores, padding_source), after_debut_moves)

        game_score = mean(scores_with_padding)

        return game_score

    def _make_move(self, llm_color: Color):
        logger.info(f'Move number: {self._current_move}')
        if self._whose_turn == llm_color:
            move = self._llm_strategy(self._llm_adapter, self._board, llm_color)
            logger.info(f'LLM move: {move}')
            self._board.push_san(move)
        else:
            result = self.__engine.play(self._board, chess.engine.Limit(depth=1, time=0.0005))
            move = result.move
            logger.info(f'Engine move: {move}')
            self._board.push(move)

    def _score_position(self, llm_color: Color):
        info = self.__engine.analyse(self._board, limit=chess.engine.Limit(depth=20))
        score = info["score"]
        centi_paws_score = score.pov(llm_color).score()
        if centi_paws_score is None:
            self.position_scores.append(MIN_POSITION_SCORE)
        else:
            paws_score = centi_paws_score / 100
            self.position_scores.append(paws_score)


def run_game(llm_color: Color, llm_strategy: Optional[str] = None) -> (Optional[GameResult], list[float], float):
    try:
        selected_strategy = strategies[llm_strategy]
    except KeyError:
        raise ValueError('Invalid strategy!')
    game = Game(selected_strategy)
    with game:
        try:
            game_result, position_scores = game.play(llm_color=llm_color)
        except RuntimeError:
            game_result, position_scores = GameResult.LOSS_INVALID_MOVE, game.position_scores
    game_score = game.get_game_score()
    return game_result, position_scores, game_score
