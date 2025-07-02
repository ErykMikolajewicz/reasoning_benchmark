import chess.engine
from chess import Board, WHITE, Color

from src.strategy import simple_move
from src.settings import settings

MAX_MOVES = settings.benchmark.MAX_MOVES


class Game:
    def __init__(self):
        self.board = Board()
        self.current_move = 1
        self.illegal_moves = 0
        self.whose_turn = WHITE
        self.position_scores = []
        self.engine = None

    def __enter__(self):
        self.engine = chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.engine.quit()
        self.engine = None

    def play(self, llm_color: Color):
        while self.current_move < MAX_MOVES and not self.board.is_game_over():
            try:
                self.__make_move(llm_color)
            except ValueError:
                print('ILLEGAL MOVE!!!!!!!!!!!!!!!!!!!!!!!')
                self.illegal_moves += 1
                if self.illegal_moves < 3:
                    continue
                else:
                    raise RuntimeError('To many invalid moves')

            self.current_move += 1
            self.__score_position()
            self.whose_turn = not self.whose_turn

        match self.board.result(), llm_color:
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
        print(f'Move number: {self.current_move}')
        if self.whose_turn == llm_color:
            move = simple_move(self.board, llm_color)
            print(f'LLM move: {move}')
            self.board.push_san(move)
        else:
            result = self.engine.play(self.board, chess.engine.Limit(depth=1, time=0.0005))
            move = result.move
            print(f'Engine move: {move}')
            self.board.push(move)

    def __score_position(self):
        info = self.engine.analyse(self.board, limit=chess.engine.Limit(depth=20))
        score = info["score"]
        self.position_scores.append(score)


def run_game(llm_color):
    game = Game()
    with game:
        try:
            game_result, scores = game.play(llm_color=llm_color)
        except RuntimeError:
            game_result, scores = None, game.position_scores
    return game_result, [score.pov(llm_color).score() for score in scores]
