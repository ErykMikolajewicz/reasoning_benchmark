import json
import logging
from pathlib import Path

from src.pydantic_models import BenchmarkingResult
from src.settings import settings
from src.share.enums import Environment
from src.utils.helpers import hash_dict

APPEND_RESULTS = settings.application.APPEND_RESULTS
ENVIRONMENT = settings.application.ENVIRONMENT

logger = logging.getLogger(__name__)


def save_result(benchmark_result: BenchmarkingResult):
    benchmark_settings = benchmark_result.benchmark_settings.model_dump()
    settings_hash = hash_dict(benchmark_settings)

    file_name = benchmark_result.model_name + "-" + settings_hash + ".json"

    match ENVIRONMENT:
        case Environment.LOCAL:
            _save_local(benchmark_result, file_name)
        case Environment.GOOGLE_CLOUD:
            _save_google_cloud(benchmark_result, file_name)


def _save_local(benchmark_result: BenchmarkingResult, file_name: str):
    result_dir = Path("results")

    result_path = result_dir / file_name

    if APPEND_RESULTS and result_path.exists():
        with open(result_path, "r", encoding="utf-8") as previous_result_file:
            previous_result = json.load(previous_result_file)
        benchmark_result = _append_results(benchmark_result, previous_result)

    with open(result_path, "w", encoding="utf-8") as result_file:
        json_str = benchmark_result.model_dump_json(indent=4)
        result_file.write(json_str)


def _save_google_cloud(benchmark_result: BenchmarkingResult, file_name: str):
    from google.cloud import storage

    client = storage.Client()

    bucket = client.bucket("llm-reasoning-benchmark-results")

    blob = bucket.blob(file_name)

    if APPEND_RESULTS and blob.exists():
        previous_result = blob.download_as_string()
        previous_result = json.loads(previous_result)
        benchmark_result = _append_results(benchmark_result, previous_result)

    json_str = benchmark_result.model_dump_json(indent=4)
    blob.upload_from_string(json_str, content_type="application/json")


def _append_results(benchmark_result: BenchmarkingResult, previous_result: dict) -> BenchmarkingResult:
    previous_result = BenchmarkingResult(**previous_result)
    benchmark_result.usage += previous_result.usage
    benchmark_result.games_data += previous_result.games_data
    return benchmark_result
