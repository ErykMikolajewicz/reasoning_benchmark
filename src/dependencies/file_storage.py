from infrastructure.file_storage import save_google_cloud, save_local
from share.enums import Environment
from share.settings.app import application_settings


def get_save_results():
    match application_settings.ENVIRONMENT:
        case Environment.LOCAL:
            return save_local
        case Environment.GOOGLE_CLOUD:
            return save_google_cloud
        case _:
            raise Exception("Invalid config value")
