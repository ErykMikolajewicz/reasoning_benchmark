import concurrent.futures
import logging
from itertools import islice

from src.chess_logic.game import run_game
from src.metrics.serialization import save_metrics
from src.models import BenchmarkingResult, GameData
from src.share.logging_config import setup_logging
from src.share.settings import settings
from src.utils.helpers import get_color_generator
from src.utils.models_adapter import LLMAdapter, models_extra_config

setup_logging()

logger = logging.getLogger(__name__)

NUM_GAMES = settings.application.PLAYS_NUMBER
MAX_WORKERS = settings.application.MAX_WORKERS
COLOR_GENERATOR = settings.application.COLOR_GENERATOR

STRATEGY = settings.benchmark.STRATEGY
BENCHMARKING_MODEL = settings.benchmark.BENCHMARKING_MODEL

color_generator = get_color_generator(COLOR_GENERATOR)
games_results: list[GameData] = []

with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    logger.info("Start creating tasks.")
    futures = [executor.submit(run_game, llm_color, STRATEGY) for llm_color in islice(color_generator, NUM_GAMES)]
    for future in concurrent.futures.as_completed(futures):
        game_data = future.result()
        games_results.append(game_data)
logger.info("Finished creating tasks.")

usage = LLMAdapter.get_usage()

logger.info(f"Prompt tokens: {usage.prompt_tokens}")
logger.info(f"Reasoning tokens: {usage.reasoning_tokens}")
logger.info(f"Text tokens: {usage.text_tokens}")
logger.info(f"Benchmark cost: {usage.total_cost_dollar}")

model_name = BENCHMARKING_MODEL.replace("/", "-")
try:
    model_extra_config = models_extra_config[model_name]
except KeyError:
    model_extra_config = {}
settings.benchmark.model_extra_config = model_extra_config

ENGINE_SETTINGS = settings.engine.model_dump()
settings.benchmark.engine_settings = ENGINE_SETTINGS

benchmarking_result = BenchmarkingResult(
    model_name=model_name, usage=usage, games_data=games_results, benchmark_settings=settings.benchmark
)

save_metrics(benchmarking_result)
