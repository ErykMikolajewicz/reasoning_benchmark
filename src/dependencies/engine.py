from chess import Color

from domain.services.moves import EngineMover
from src.share.settings.engine import engine_settings


def get_engine_mover(engine_color: Color) -> EngineMover:
    analyse_depth = engine_settings.ANALYSE_DEPTH
    acceptance_threshold = engine_settings.MOVE_ACCEPTANCE_THRESHOLD_CENTI_PAWS
    multi_pv = engine_settings.MULTI_PV

    return EngineMover(engine_color, analyse_depth, multi_pv, acceptance_threshold)
