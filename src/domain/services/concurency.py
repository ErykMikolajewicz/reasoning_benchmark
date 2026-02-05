import concurrent.futures
import logging
from collections.abc import Generator
from dataclasses import dataclass
from itertools import islice

from chess import Color

from domain.services.running import run_game
from domain.value_objects.pydantic_models import GameData

logger = logging.getLogger(__name__)


@dataclass
class GamesRunner:
    num_games: int
    max_workers: int
    color_generator: Generator[Color, None, None]

    def run_games(self) -> list[GameData]:

        games_results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            logger.info("Start creating tasks.")
            colors = islice(self.color_generator, self.num_games)
            futures = [executor.submit(run_game, llm_color) for llm_color in colors]
            for future in concurrent.futures.as_completed(futures):
                game_data = future.result()
                games_results.append(game_data)
        logger.info("Finished creating tasks.")

        return games_results
