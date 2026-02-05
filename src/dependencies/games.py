from dependencies.engine import get_engine_mover
from dependencies.llm import get_llm_mover
from domain.services.game import Game
from share.settings.benchmark import benchmark_settings


def get_game(llm_color) -> Game:
    llm_mover = get_llm_mover(llm_color)

    engine_color = not llm_color
    engine_mover = get_engine_mover(engine_color)

    max_ply = benchmark_settings.MAX_PLY

    return Game(llm_mover, llm_color, engine_mover, max_ply)
