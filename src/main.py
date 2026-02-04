import concurrent.futures
import logging
from itertools import islice

from domain.game import run_game
from domain.serialization import save_result
from domain.utils.helpers import get_color_generator
from domain.value_objects.pydantic_models import BenchmarkingResult, GameData
from infrastructure.models_adapter import LLMAdapter, models_extra_config
from share.logging_config import setup_logging
from share.settings.app import application_settings
from share.settings.benchmark import benchmark_settings
from share.settings.engine import engine_settings

setup_logging()

logger = logging.getLogger(__name__)

NUM_GAMES = application_settings.PLAYS_NUMBER
MAX_WORKERS = application_settings.MAX_WORKERS
COLOR_GENERATOR = application_settings.COLOR_GENERATOR

STRATEGY = benchmark_settings.STRATEGY
BENCHMARKING_MODEL = benchmark_settings.MODEL

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
benchmark_settings.model_extra_config = model_extra_config

ENGINE_SETTINGS = engine_settings.model_dump()
benchmark_settings.engine_settings = ENGINE_SETTINGS

benchmarking_result = BenchmarkingResult(
    model_name=model_name,
    usage=usage,
    games_data=games_results,
    benchmark_settings=benchmark_settings,
)

save_result(benchmarking_result)
