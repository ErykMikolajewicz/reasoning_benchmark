from typing import Callable, TypeAlias

from domain.value_objects.board import BoardInfo
from infrastructure.models_adapter import LLMAdapter

GameStrategy: TypeAlias = Callable[[LLMAdapter, BoardInfo, dict], str]
