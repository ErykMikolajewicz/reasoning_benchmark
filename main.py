import math
from itertools import cycle, islice

from dotenv import load_dotenv; load_dotenv()
from chess import WHITE, BLACK
import matplotlib.pyplot as plt
import concurrent.futures

from src.game import run_game
from src.settings import settings

NUM_GAMES = settings.benchmark.PLAYS_NUMBER
STRATEGY = settings.benchmark.STRATEGY

color_generator = cycle([WHITE, BLACK])
results = []
all_scores = []

with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_GAMES) as executor:
    futures = [executor.submit(run_game, llm_color, STRATEGY) for llm_color in islice(color_generator, NUM_GAMES)]
    for future in concurrent.futures.as_completed(futures):
        game_result, scores = future.result()
        results.append(game_result)
        all_scores.append(scores)

n_cols = math.ceil(math.sqrt(NUM_GAMES))
n_rows = math.ceil(NUM_GAMES / n_cols)

fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(4*n_cols, 3*n_rows), sharex=False, sharey=True)
if NUM_GAMES > 1:
    axes = axes.flatten()
else:
    axes = [axes]

for i, (scores, ax) in enumerate(zip(all_scores, axes)):
    ax.plot(scores)
    ax.set_title(f'Game {i+1}')
    ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
    ax.set_xlabel('Move')
    ax.set_ylabel('Score')

for ax in axes[len(all_scores):]:
    ax.axis('off')

plt.tight_layout()
plt.show()

print("Results:", results)
print("All scores:", all_scores)

