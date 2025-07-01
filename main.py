from dotenv import load_dotenv; load_dotenv()
from chess import WHITE, Board
import chess.engine
import matplotlib.pyplot as plt

from src.strategy import llm_move

MAX_MOVES = 30


def play_game(llm_color=WHITE):
    board = Board()
    illegal = 0
    whose_turn = WHITE
    position_scores = []
    with chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish") as engine:
        for loop_number in range(1, MAX_MOVES):
            if whose_turn == llm_color:
                move_san = llm_move(board, llm_color)
                try:
                    board.push_san(move_san)
                except ValueError:
                    print(f'INVALID MOVE!!!!!!!!!!!!\n{move_san}')
                    illegal += 1
                    if illegal >= 3:
                        return 0, position_scores
                    continue
                whose_turn = not whose_turn
                info = engine.analyse(board, limit=chess.engine.Limit(depth=20))
                score = info["score"]
                position_scores.append(score)
                print(f'Move number: {loop_number - illegal}')
                print(f'LLM move: {move_san}')
            else:
                result = engine.play(board, chess.engine.Limit(depth=1)) # Should be very stupid
                move = result.move
                print(f'Engine move: {move}')
                board.push(move)
                whose_turn = not whose_turn

            if board.is_game_over():
                break
    if board.result() == "1-0":
        return 1, position_scores if llm_color else 0, position_scores
    if board.result() == "0-1":
        return 0, position_scores if llm_color else 1, position_scores
    return 0.5, position_scores


if __name__ == "__main__":
    game_result, scores = play_game(llm_color=WHITE)
    scores = [score.pov(WHITE).score() for score in scores]
    plt.plot(scores)
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    plt.show()
    print(game_result)
    print(scores)
