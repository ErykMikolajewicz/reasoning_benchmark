from dependencies.file_storage import get_save_results
from domain.utils.helpers import hash_dict
from domain.value_objects.pydantic_models import BenchmarkingResult


def save_result(benchmark_result: BenchmarkingResult):
    benchmark_settings = benchmark_result.benchmark_settings.model_dump()
    settings_hash = hash_dict(benchmark_settings)

    file_name = benchmark_result.model_name + "-" + settings_hash + ".json"

    save_results = get_save_results()
    save_results(benchmark_result, file_name)
