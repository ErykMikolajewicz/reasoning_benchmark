import math

from dotenv import load_dotenv; load_dotenv()
from chess import WHITE
import matplotlib.pyplot as plt
import concurrent.futures

from src.game import Game

NUM_GAMES = 12

def run_game(llm_color):
    game = Game()
    with game:
        try:
            game_result, scores = game.play(llm_color=llm_color)
        except RuntimeError:
            game_result, scores = None, game.position_scores
    return game_result, [score.pov(llm_color).score() for score in scores]

llm_color = WHITE  # lub wylosuj np. random.choice([WHITE, BLACK])
results = []
all_scores = []

with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_GAMES) as executor:
    futures = [executor.submit(run_game, llm_color) for _ in range(NUM_GAMES)]
    for future in concurrent.futures.as_completed(futures):
        game_result, scores = future.result()
        results.append(game_result)
        all_scores.append(scores)

ncols = math.ceil(math.sqrt(NUM_GAMES))
nrows = math.ceil(NUM_GAMES / ncols)

fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(4*ncols, 3*nrows), sharex=False, sharey=True)
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

