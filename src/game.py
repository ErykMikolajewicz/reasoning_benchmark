from typing import Callable, Optional

import chess.engine
from chess import Board, WHITE, Color

from src.strategy import strategies
from src.settings import settings
from src.enums import GameResult
from src.conts import MAX_POSITION_SCORE, WIN_BONUS, MIN_POSITION_SCORE

MAX_MOVES = settings.benchmark.MAX_MOVES


class Game:
    def __init__(self, llm_strategy: Callable[[Board, Color], str]):
        self._board = Board()
        self._current_move = 1
        self._illegal_moves = 0
        self._whose_turn = WHITE
        self.position_scores: list[float] = []
        self._engine = None
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
        while self._current_move < MAX_MOVES and not self._board.is_game_over():
            try:
                self._make_move(llm_color)
            except ValueError:
                print('ILLEGAL MOVE!!!!!!!!!!!!!!!!!!!!!!!')
                self._illegal_moves += 1
                if self._illegal_moves < 3:
                    continue
                else:
                    self._is_game_ended = True
                    self._match_result = GameResult.LOSS
                    raise RuntimeError('To many invalid moves')

            self._current_move += 1
            self._score_position(llm_color)
            self._whose_turn = not self._whose_turn

        self._is_game_ended = True

        match self._board.result(), llm_color:
            case "*", _:
                match_result = None
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
            raise RuntimeError('Game not ended!')

        match self._match_result:
            case GameResult.WIN:
                return MAX_MOVES * MAX_POSITION_SCORE + WIN_BONUS
            case GameResult.TIE:
                return MAX_MOVES * MAX_POSITION_SCORE

        adjustment_score = []
        for position_score in self.position_scores:
            adjustment_to_0_position_score = position_score - MIN_POSITION_SCORE
            adjustment_score.append(adjustment_to_0_position_score)

        game_score = sum(adjustment_score)

        return game_score

    def _make_move(self, llm_color: Color):
        print(f'Move number: {self._current_move}')
        if self._whose_turn == llm_color:
            move = self._llm_strategy(self._board, llm_color)
            print(f'LLM move: {move}')
            self._board.push_san(move)
        else:
            result = self.__engine.play(self._board, chess.engine.Limit(depth=1, time=0.0005))
            move = result.move
            print(f'Engine move: {move}')
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
            game_result, position_scores = None, game.position_scores
    game_score = game.get_game_score()
    return game_result, position_scores, game_score
