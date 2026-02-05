import logging

from dependencies.file_storage import get_save_results
from domain.utils.helpers import hash_dict
from domain.value_objects.pydantic_models import BenchmarkingResult
from infrastructure.models_adapter import LLMAdapter, models_extra_config
from share.settings.benchmark import benchmark_settings
from share.settings.engine import engine_settings

logger = logging.getLogger(__name__)

BENCHMARKING_MODEL = benchmark_settings.MODEL


def prepare_results(games_results) -> BenchmarkingResult:
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

    engine_settings_json = engine_settings.model_dump()
    benchmark_settings.engine_settings = engine_settings_json

    benchmarking_result = BenchmarkingResult(
        model_name=model_name,
        usage=usage,
        games_data=games_results,
        benchmark_settings=benchmark_settings,
    )

    return benchmarking_result


def save_result(benchmark_result: BenchmarkingResult):
    benchmark_settings_json = benchmark_result.benchmark_settings.model_dump()
    settings_hash = hash_dict(benchmark_settings_json)

    file_name = benchmark_result.model_name + "-" + settings_hash + ".json"

    save_results = get_save_results()
    save_results(benchmark_result, file_name)
