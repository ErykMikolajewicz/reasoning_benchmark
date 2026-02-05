from pathlib import Path


class LocalResultSaver:
    def __init__(self, result_dir: Path = Path("results")):
        self._result_dir = result_dir

    def save_result(self, file_name: str, benchmark_result: str):
        result_path = self._result_dir / file_name

        with open(result_path, "w", encoding="utf-8") as result_file:
            result_file.write(benchmark_result)

    def get_result(self, file_name: str) -> str | None:
        result_path = self._result_dir / file_name

        try:
            with open(result_path, "r", encoding="utf-8") as result_file:
                benchmark_result = result_file.read()
        except FileNotFoundError:
            benchmark_result = None

        return benchmark_result
