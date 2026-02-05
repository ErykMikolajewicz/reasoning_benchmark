from dependencies.file_storage import get_result_storage
from domain.services.serialization import ResultSaver
from share.settings.app import application_settings
from share.settings.benchmark import benchmark_settings


def get_result_saver() -> ResultSaver:
    append_results = application_settings.APPEND_RESULTS
    model = benchmark_settings.MODEL
    result_storage = get_result_storage()
    return ResultSaver(model, append_results, result_storage)
