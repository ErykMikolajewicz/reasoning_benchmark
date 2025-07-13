from pathlib import Path

from src.metrics.models import BenchmarkingResult

def save_metrics(benchmark_result: BenchmarkingResult):
    result_dir = Path('results')
    result_dir.mkdir(exist_ok=True)
    result_path = result_dir / (benchmark_result.model_name + '.json')
    with open(result_path, 'w', encoding='utf-8') as result_file:
        json_str = benchmark_result.model_dump_json()
        result_file.write(json_str)
