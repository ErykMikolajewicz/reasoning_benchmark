import hashlib
import json
import logging
from dataclasses import asdict
from decimal import Decimal

from domain.protocols import ResultStorage
from domain.value_objects.benchmark import BenchmarkConfig, EngineSettings
from domain.value_objects.results import BenchmarkingResult, ModelUsage
from infrastructure.models_adapter import LLMAdapter, models_extra_config
from share.settings.benchmark import benchmark_settings
from share.settings.engine import engine_settings

logger = logging.getLogger(__name__)


class ResultSaver:
    def __init__(self, model: str, append_results: bool, result_storage: ResultStorage):
        self._model = model
        self._append_results = append_results
        self._result_storage = result_storage

    def save_results(self, games_results):
        usage = LLMAdapter.get_usage()

        logger.info(f"Prompt tokens: {usage.prompt_tokens}")
        logger.info(f"Reasoning tokens: {usage.reasoning_tokens}")
        logger.info(f"Text tokens: {usage.text_tokens}")
        logger.info(f"Benchmark cost: {usage.total_cost_dollar}")

        benchmark_config = self._gather_benchmark_config()

        config_hash = self._get_config_hash(benchmark_config)

        file_name = self._model + "-" + config_hash + ".json"

        if self._append_results:
            benchmarking_result = self._result_storage.get_result(file_name)
            if benchmarking_result is None:
                benchmarking_result = BenchmarkingResult(benchmark_config, usage, games_results)
            else:
                benchmarking_result = json.loads(benchmarking_result)
                cost_dollars = benchmarking_result["usage"]["total_cost_dollar"]
                benchmarking_result["usage"]["total_cost_dollar"] = Decimal(cost_dollars)
                benchmarking_result["usage"] = ModelUsage(**benchmarking_result["usage"])
                benchmarking_result = BenchmarkingResult(**benchmarking_result)
                benchmarking_result.usage = benchmarking_result.usage + usage
                benchmarking_result.games_data.extend(games_results)
        else:
            benchmarking_result = BenchmarkingResult(benchmark_config, usage, games_results)

        benchmarking_result = asdict(benchmarking_result)
        benchmarking_result = json.dumps(benchmarking_result, default=str)

        self._result_storage.save_result(file_name, benchmarking_result)

    def _gather_benchmark_config(self) -> BenchmarkConfig:
        model = self._model
        strategy = benchmark_settings.STRATEGY
        max_ply = benchmark_settings.MAX_PLY
        max_illegal_moves = benchmark_settings.MAX_ILLEGAL_MOVES

        analyse_depth = engine_settings.ANALYSE_DEPTH
        acceptance_threshold = engine_settings.MOVE_ACCEPTANCE_THRESHOLD_CENTI_PAWS
        multi_pv = engine_settings.MULTI_PV
        engine_settings_dataclass = EngineSettings(analyse_depth, acceptance_threshold, multi_pv)

        try:
            model_extra_config = models_extra_config[self._model]
        except KeyError:
            model_extra_config = {}
        benchmark_settings.model_extra_config = model_extra_config

        benchmark_config = BenchmarkConfig(
            model, strategy, max_ply, max_illegal_moves, engine_settings_dataclass, model_extra_config
        )

        return benchmark_config

    @staticmethod
    def _get_config_hash(benchmark_config: BenchmarkConfig) -> str:
        config = asdict(benchmark_config)
        config = json.dumps(config, sort_keys=True)
        config = config.encode()

        config_hash = hashlib.sha256(config)
        config_hash = config_hash.hexdigest()

        return config_hash
