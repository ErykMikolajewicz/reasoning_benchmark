from domain.protocols import ResultStorage
from share.enums import Environment
from share.settings.app import application_settings


def get_result_storage() -> ResultStorage:
    match application_settings.ENVIRONMENT:
        case Environment.LOCAL:
            from infrastructure.local_result_saver import LocalResultSaver

            return LocalResultSaver()
        case Environment.GOOGLE_CLOUD:
            from infrastructure.gc_result_saver import GoogleCloudResultSaver

            return GoogleCloudResultSaver()
        case _:
            raise Exception("Invalid config value")
