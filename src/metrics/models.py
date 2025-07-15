from decimal import Decimal
from typing import cast

from pydantic import BaseModel

from src.share.enums import GameResult
from src.share.settings import BenchmarkSettings

addable_types = {int, float, Decimal, list}


class AddableModel(BaseModel):
    def __add__(self, other):
        model_class = self.__class__
        if not isinstance(other, model_class):
            return NotImplemented
        user_fields = cast(dict, model_class.model_fields)

        values = {}
        for field in user_fields.keys():
            current_value = getattr(self, field)
            field_type = type(current_value)
            if field_type in addable_types:
                value_to_add = getattr(other, field)
                new_value = current_value + value_to_add
            else:
                new_value = current_value
            values[field] = new_value
        return model_class(**values)


class ModelUsage(AddableModel):
    prompt_tokens: int = 0
    reasoning_tokens: int = 0
    text_tokens: int = 0
    total_cost_dollar: Decimal = Decimal(0.)


class BenchmarkingResult(BaseModel):
    model_name: str
    usage: ModelUsage
    scores: list[float]
    party_results: list[GameResult]
    benchmark_settings: BenchmarkSettings
