from typing import Callable, TypeAlias

from src.utils.models_adapter import LLMAdapter
from src.domain.schemas import BoardInfo

GameStrategy: TypeAlias = Callable[[LLMAdapter, BoardInfo, dict], str]
