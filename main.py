import math
from statistics import mean
from itertools import cycle, islice

from dotenv import load_dotenv; load_dotenv()
from chess import WHITE, BLACK
import matplotlib.pyplot as plt
import concurrent.futures

from src.game import run_game
from src.settings import settings
from src.models_adapter import LLMAdapter
from src.logging_config import setup_logging

NUM_GAMES = settings.benchmark.PLAYS_NUMBER
STRATEGY = settings.benchmark.STRATEGY
MAX_WORKERS = settings.application.MAX_WORKERS

setup_logging()

color_generator = cycle([WHITE, BLACK])
results = []
all_scores = []
games_score = []

with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(run_game, llm_color, STRATEGY) for llm_color in islice(color_generator, NUM_GAMES)]
    for future in concurrent.futures.as_completed(futures):
        game_result, position_scores, game_score = future.result()
        results.append(game_result)
        all_scores.append(position_scores)
        games_score.append(game_score)


n_cols = math.ceil(math.sqrt(NUM_GAMES))
n_rows = math.ceil(NUM_GAMES / n_cols)
average_game_score = mean(games_score)

fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(4*n_cols, 3*n_rows), sharex=False, sharey=True)
if NUM_GAMES > 1:
    axes = axes.flatten()
else:
    axes = [axes]

for i, (position_scores, ax) in enumerate(zip(all_scores, axes)):
    ax.plot(range(1, len(position_scores) + 1), position_scores)
    ax.set_title(f'Game {i+1}')
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.set_xlabel('Move')
    ax.set_ylabel('Score')

plt.tight_layout()
plt.show()

print("Results:", results)
print('Games scores:', games_score)
print('Average score:', average_game_score)

prompt_tokens, reasoning_tokens, text_tokens, total_cost = LLMAdapter.get_usage()
print('Prompt tokens:', prompt_tokens)
print('Reasoning tokens:', reasoning_tokens)
print('Text tokens:', text_tokens)
print('Benchmark cost:', total_cost)
