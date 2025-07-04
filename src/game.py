from typing import Callable, Optional

import chess.engine
from chess import Board, WHITE, Color

from src.strategy import strategies
from src.settings import settings

MAX_MOVES = settings.benchmark.MAX_MOVES


class Game:
    def __init__(self, llm_strategy: Callable[[Board, Color], str]):
        self.__board = Board()
        self.__current_move = 1
        self.__illegal_moves = 0
        self.__whose_turn = WHITE
        self.position_scores = []
        self.__engine = None
        self.__llm_strategy = llm_strategy

    def __enter__(self):
        self.__engine = chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__engine.quit()
        self.__engine = None

    def play(self, llm_color: Color):
        while self.__current_move < MAX_MOVES and not self.__board.is_game_over():
            try:
                self.__make_move(llm_color)
            except ValueError:
                print('ILLEGAL MOVE!!!!!!!!!!!!!!!!!!!!!!!')
                self.__illegal_moves += 1
                if self.__illegal_moves < 3:
                    continue
                else:
                    raise RuntimeError('To many invalid moves')

            self.__current_move += 1
            self.__score_position()
            self.__whose_turn = not self.__whose_turn

        match self.__board.result(), llm_color:
            case "*", _:
                match_result = None
            case "1-0", True:
                match_result = 1
            case "1-0", False:
                match_result = 0
            case "0-1", True:
                match_result = 0
            case "0-1", False:
                match_result = 1
            case _:
                match_result = 0.5

        return match_result, self.position_scores


    def __make_move(self, llm_color: Color):
        print(f'Move number: {self.__current_move}')
        if self.__whose_turn == llm_color:
            move = self.__llm_strategy(self.__board, llm_color)
            print(f'LLM move: {move}')
            self.__board.push_san(move)
        else:
            result = self.__engine.play(self.__board, chess.engine.Limit(depth=1, time=0.0005))
            move = result.move
            print(f'Engine move: {move}')
            self.__board.push(move)

    def __score_position(self):
        info = self.__engine.analyse(self.__board, limit=chess.engine.Limit(depth=20))
        score = info["score"]
        self.position_scores.append(score)


def run_game(llm_color: Color, llm_strategy: Optional[str] = None):
    try:
        selected_strategy = strategies[llm_strategy]
    except KeyError:
        raise ValueError('Invalid strategy!')
    game = Game(selected_strategy)
    with game:
        try:
            game_result, scores = game.play(llm_color=llm_color)
        except RuntimeError:
            game_result, scores = None, game.position_scores
    return game_result, [score.pov(llm_color).score() for score in scores]
