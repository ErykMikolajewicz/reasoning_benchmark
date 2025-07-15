import math
from statistics import mean
from itertools import cycle, islice

from dotenv import load_dotenv; load_dotenv()
from chess import WHITE, BLACK
import matplotlib.pyplot as plt
import concurrent.futures

from src.share.logging_config import setup_logging
from src.chess_logic.game import run_game
from src.share.settings import settings
from src.utils.models_adapter import LLMAdapter
from src.metrics.serialization import save_metrics
from src.metrics.models import BenchmarkingResult

setup_logging()

NUM_GAMES = settings.application.PLAYS_NUMBER
STRATEGY = settings.benchmark.STRATEGY
MAX_WORKERS = settings.application.MAX_WORKERS
BENCHMARKING_MODEL = settings.benchmark.BENCHMARKING_MODEL

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

usage = LLMAdapter.get_usage()

print("Results:", results)
print('Games scores:', games_score)
print('Average score:', average_game_score)

print('Prompt tokens:', usage.prompt_tokens)
print('Reasoning tokens:', usage.reasoning_tokens)
print('Text tokens:', usage.text_tokens)
print('Benchmark cost:', usage.total_cost_dollar)

model_name = BENCHMARKING_MODEL.replace('/', '-')

benchmarking_result = BenchmarkingResult(model_name=model_name,
                                         usage=usage,
                                         scores=games_score,
                                         party_results=results,
                                         benchmark_settings=settings.benchmark)
save_metrics(benchmarking_result)
