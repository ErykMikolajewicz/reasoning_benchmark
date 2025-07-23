from typing import Callable, TypeAlias

from src.utils.models_adapter import LLMAdapter

GameStrategy: TypeAlias = Callable[[LLMAdapter, str], str]
