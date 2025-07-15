from pathlib import Path
import json
import logging
from uuid import uuid4

from src.metrics.models import BenchmarkingResult
from src.share.settings import settings

APPEND_RESULTS = settings.application.APPEND_RESULTS

logger = logging.getLogger(__name__)

def save_metrics(benchmark_result: BenchmarkingResult):
    result_dir = Path('results')
    result_dir.mkdir(exist_ok=True)
    result_path = result_dir / (benchmark_result.model_name + '.json')

    previous_result = None
    if APPEND_RESULTS:
        try:
            with open(result_path, 'r', encoding='utf-8') as previous_result_file:
                previous_result = json.load(previous_result_file)
                previous_result = BenchmarkingResult(**previous_result)
        except FileNotFoundError:
            pass

    if previous_result is not None:
        previous_settings = previous_result.benchmark_settings
        current_settings = benchmark_result.benchmark_settings

        if previous_settings != current_settings:
            logger.error('Inconsistent benchmark settings, during appending!')
            error_id = str(uuid4())
            result_path = result_dir / (benchmark_result.model_name + '-inconsistent-error-' + error_id + '.json')

        total_usage = benchmark_result.usage + previous_result.usage
        benchmark_result.usage = total_usage

        new_scores = previous_result.scores
        benchmark_result.scores.extend(new_scores)

        new_party_results = previous_result.party_results
        benchmark_result.party_results.extend(new_party_results)


    with open(result_path, 'w', encoding='utf-8') as result_file:
        json_str = benchmark_result.model_dump_json(indent=4)
        result_file.write(json_str)
