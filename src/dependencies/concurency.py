from dependencies.colors import get_color_generator
from domain.services.concurency import GamesRunner
from share.settings.app import application_settings


def get_games_runner() -> GamesRunner:
    color_generator = get_color_generator()

    max_workers = application_settings.MAX_WORKERS
    plays_number = application_settings.PLAYS_NUMBER

    return GamesRunner(max_workers, plays_number, color_generator)
