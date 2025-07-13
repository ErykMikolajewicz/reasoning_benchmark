from decimal import Decimal, ROUND_UP
import threading
import logging

from litellm import ModelResponse, completion, completion_cost

from src.metrics.models import ModelUsage

logger = logging.getLogger(__name__)


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
    def get_usage(cls) -> ModelUsage:
        all_usage = ModelUsage()
        with threading.Lock():
            threads_usage = cls._threads_adapters.values()
            for thread_usage in threads_usage:
                models_usage = thread_usage.values()
                for model_usage in models_usage:
                    all_usage += model_usage
                    # all_usage.prompt_tokens += model_usage.prompt_tokens
                    # all_usage.reasoning_tokens += model_usage.reasoning_tokens
                    # all_usage.text_tokens += model_usage.text_tokens
                    # all_usage.total_cost_dollar += model_usage.total_cost_dollar
        return all_usage
