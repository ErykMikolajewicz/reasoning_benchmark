from dotenv import load_dotenv; load_dotenv()
from chess import WHITE
import matplotlib.pyplot as plt

from src.game import Game

llm_color = WHITE
game = Game()
with game:
    try:
        game_result, scores = game.play(llm_color=llm_color)
    except RuntimeError:
        game_result, scores = None, game.position_scores

scores = [score.pov(llm_color).score() for score in scores]
plt.plot(scores)
plt.gca().xaxis.set_major_locator(plt.MaxNLocator(integer=True))
plt.show()
print(game_result)
print(scores)
