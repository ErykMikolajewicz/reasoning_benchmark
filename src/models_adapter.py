from decimal import Decimal, ROUND_UP
from dataclasses import dataclass
import threading
import logging

from litellm import ModelResponse, completion, completion_cost

logger = logging.getLogger(__name__)


@dataclass
class ModelUsage:
    prompt_tokens: int = 0
    reasoning_tokens: int = 0
    text_tokens: int = 0
    total_cost_dollar: Decimal = Decimal(0.)


class LLMAdapter:
    _threads_adapters = {}

    def __init__(self):
        thread_id = threading.get_ident()
        threads_adapters = self.__class__._threads_adapters
        with threading.Lock():
            try:
                self.models_usage = threads_adapters[thread_id]
            except KeyError:
                self.models_usage = {}
                threads_adapters[thread_id] = self.models_usage

    def send_messages(self, model: str, messages: list) -> str:
        response = completion(
            model=model,
            messages=messages)

        answer = response.choices[0].message.content
        logger.debug(answer)
        logger.debug(f'Request usage: {response['usage']}')

        self._add_tokens(model, response)

        return answer

    def _add_tokens(self, model: str, response: ModelResponse):

        try:
            model_usage = self.models_usage[model]
        except KeyError:
            model_usage = ModelUsage()
            self.models_usage[model] = model_usage

        model_usage.prompt_tokens += response.usage.prompt_tokens
        model_usage.text_tokens += response.usage.completion_tokens_details.text_tokens
        model_usage.reasoning_tokens += response.usage.completion_tokens_details.reasoning_tokens

        cost_float = completion_cost(response, model)
        cost_decimal = Decimal(cost_float)

        model_usage.total_cost_dollar += cost_decimal.quantize(Decimal('0.01'), rounding=ROUND_UP)

    @classmethod
    def get_usage(cls):
        prompt_tokens, reasoning_tokens, text_tokens, total_cost = 0, 0, 0, Decimal(0.)
        with threading.Lock():
            threads_usage = cls._threads_adapters.values()
            for thread_usage in threads_usage:
                models_usage = thread_usage.values()
                for model_usage in models_usage:
                    prompt_tokens += model_usage.prompt_tokens
                    reasoning_tokens += model_usage.reasoning_tokens
                    text_tokens += model_usage.text_tokens
                    total_cost += model_usage.total_cost_dollar
        return prompt_tokens, reasoning_tokens, text_tokens, total_cost
