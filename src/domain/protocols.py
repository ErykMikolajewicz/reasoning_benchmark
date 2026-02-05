from typing import Protocol


class ResultStorage(Protocol):
    def save_result(self, file_name: str, benchmark_result: str): ...

    def get_result(self, file_name: str) -> str | None: ...
