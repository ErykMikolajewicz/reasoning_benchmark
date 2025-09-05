import math
import os
from itertools import chain, islice, repeat
from statistics import mean

import chess.engine
import matplotlib.pyplot as plt
import numpy as np
from chess import Board, Color

from src.share.conts import MAX_POSITION_SCORE, MIN_POSITION_SCORE, TIE_SCORE
from src.share.enums import GameResult
from src.share.settings import settings

MAX_MOVES = settings.benchmark.MAX_MOVES
DEBUT_OFFSET = settings.analyze.DEBUT_OFFSET

engine = chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")
_CPU_COUNT = os.cpu_count()
engine.configure({"Threads": _CPU_COUNT})


def get_game_score(position_scores: list[float], match_result: GameResult) -> float:
    try:
        relevant_scores = position_scores[DEBUT_OFFSET:]
    except IndexError:
        relevant_scores = []

    after_debut_moves = MAX_MOVES - DEBUT_OFFSET

    match match_result:
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
            raise RuntimeError("Invalid game result status!")

    scores_with_padding = islice(chain(relevant_scores, padding_source), after_debut_moves)

    game_score = mean(scores_with_padding)

    return game_score


def score_positions(moves: list[str], llm_color: Color) -> list[float]:
    board = Board()
    scores = []
    for move in moves:
        try:
            board.push_san(move)
        except ValueError:
            return scores
        info = engine.analyse(board, limit=chess.engine.Limit(depth=20))
        score = info["score"]
        score_llm_point_of_view = score.pov(llm_color)
        centi_paws_score = score_llm_point_of_view.score()
        if centi_paws_score is None:
            party_result = board.result()
            match party_result, llm_color:
                case "*", _:
                    moves_to_mate = score_llm_point_of_view.moves
                    if moves_to_mate > 0:
                        scores.append(MAX_POSITION_SCORE)
                    elif moves_to_mate < 0:
                        scores.append(MIN_POSITION_SCORE)
                    else:
                        raise RuntimeError("Invalid game status!")
                case "1-0", True:
                    scores.append(MAX_POSITION_SCORE)
                case "1-0", False:
                    scores.append(MIN_POSITION_SCORE)
                case "0-1", True:
                    scores.append(MIN_POSITION_SCORE)
                case "0-1", False:
                    scores.append(MAX_POSITION_SCORE)
                case _:
                    scores.append(TIE_SCORE)
        else:
            paws_score = centi_paws_score / 100
            scores.append(paws_score)
    return scores


def plot_parties_scores(parties_scores: list[list[float]], label: str):
    num_games = len(parties_scores)
    n_cols = math.ceil(math.sqrt(num_games))
    n_rows = math.ceil(num_games / n_cols)

    fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(4 * n_cols, 3 * n_rows), sharex=False, sharey=True)
    if num_games > 1:
        axes = axes.flatten()
    else:
        axes = [axes]

    for i, (position_scores, ax) in enumerate(zip(parties_scores, axes)):
        ax.plot(range(1, len(position_scores[:-2]) + 1), position_scores[:-2])
        ax.set_title(f"Game {i+1}")
        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        ax.set_xlabel("Move")
        ax.set_ylabel("Score")

    fig.suptitle(label, fontsize=16)

    plt.tight_layout(rect=(0, 0, 1, 0.95))
    plt.show()
