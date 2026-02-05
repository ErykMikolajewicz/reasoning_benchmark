from chess import Color

from dependencies.games import get_game
from domain.value_objects.pydantic_models import GameData


def run_game(llm_color: Color) -> GameData:
    game = get_game(llm_color)
    game_result, game_history = game.play()

    game_data = GameData(result=game_result, history=game_history, llm_color=llm_color)
    return game_data
