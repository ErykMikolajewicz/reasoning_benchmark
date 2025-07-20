import concurrent.futures
import math
from itertools import cycle, islice
from statistics import mean

import matplotlib.pyplot as plt
from chess import BLACK, WHITE

from src.chess_logic.game import run_game
from src.models import BenchmarkingResult, GameData
from src.metrics.serialization import save_metrics
from src.share.logging_config import setup_logging
from src.share.settings import settings
from src.utils.models_adapter import LLMAdapter, models_extra_config

setup_logging()

NUM_GAMES = settings.application.PLAYS_NUMBER
STRATEGY = settings.benchmark.STRATEGY
MAX_WORKERS = settings.application.MAX_WORKERS
BENCHMARKING_MODEL = settings.benchmark.BENCHMARKING_MODEL

color_generator = cycle([WHITE, BLACK])
games_results: list[GameData] = []

with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = [executor.submit(run_game, llm_color, STRATEGY) for llm_color in islice(color_generator, NUM_GAMES)]
    for future in concurrent.futures.as_completed(futures):
        game_data = future.result()
        games_results.append(game_data)

all_scores = [game_data.position_scores for game_data in games_results]
games_score = [game_data.score for game_data in games_results]
party_results = [game_data.result for game_data in games_results]

n_cols = math.ceil(math.sqrt(NUM_GAMES))
n_rows = math.ceil(NUM_GAMES / n_cols)
average_game_score = mean(games_score)

fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(4 * n_cols, 3 * n_rows), sharex=False, sharey=True)
if NUM_GAMES > 1:
    axes = axes.flatten()
else:
    axes = [axes]

for i, (position_scores, ax) in enumerate(zip(all_scores, axes)):
    ax.plot(range(1, len(position_scores) + 1), position_scores)
    ax.set_title(f"Game {i+1}")
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.set_xlabel("Move")
    ax.set_ylabel("Score")

plt.tight_layout()
plt.show()

usage = LLMAdapter.get_usage()

print("Games scores:", games_score)
print("Average score:", average_game_score)

print("Prompt tokens:", usage.prompt_tokens)
print("Reasoning tokens:", usage.reasoning_tokens)
print("Text tokens:", usage.text_tokens)
print("Benchmark cost:", usage.total_cost_dollar)

model_name = BENCHMARKING_MODEL.replace("/", "-")
try:
    model_extra_config = models_extra_config[model_name]
except KeyError:
    model_extra_config = {}

settings.benchmark.MODEL_EXTRA_CONFIG = model_extra_config


benchmarking_result = BenchmarkingResult(
    model_name=model_name, usage=usage, games_data=games_results, benchmark_settings=settings.benchmark
)
save_metrics(benchmarking_result)
