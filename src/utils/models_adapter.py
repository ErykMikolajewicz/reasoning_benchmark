import json
import logging
import threading
from decimal import ROUND_UP, Decimal
from pathlib import Path

from dotenv import load_dotenv
from litellm import ModelResponse, completion, completion_cost
from litellm.exceptions import InternalServerError, RateLimitError, Timeout
from tenacity import (
    after_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random,
)

from src.pydantic_models import ModelUsage
from src.settings import settings

load_dotenv("settings/api_keys.env")

RETRY_NUMBER = settings.application.RETRY_NUMBER
LLM_TIMEOUT = settings.application.LLM_TIMEOUT
MINIMUM_WAIT_SECONDS = settings.application.MINIMUM_WAIT_SECONDS
MAXIMUM_WAIT_SECONDS = settings.application.MAXIMUM_WAIT_SECONDS

logger = logging.getLogger(__name__)

models_extra_config = {}
models_params_dir = Path("models_params")
models_config_paths = models_params_dir.glob("*.json")
for extra_config_path in models_config_paths:
    with open(extra_config_path, "r") as config_file:
        extra_config = json.load(config_file)
    model_name = extra_config_path.stem
    models_extra_config[model_name] = extra_config


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

    @retry(
        retry=retry_if_exception_type((RateLimitError, Timeout, InternalServerError)),
        wait=wait_random(MINIMUM_WAIT_SECONDS, MAXIMUM_WAIT_SECONDS),
        stop=stop_after_attempt(RETRY_NUMBER),
        after=after_log(logger, logging.WARNING),
    )
    def send_messages(self, model: str, messages: list, response_format: dict | None = None) -> str:
        for message in messages:
            log = f"Message type: {message['role']}, message:\n{message['content']}"
            logger.debug(log)

        model_file_name = model.replace("/", "-")
        model_params = models_extra_config.get(model_file_name, {})

        try:
            response = completion(timeout=LLM_TIMEOUT,
                                  model=model,
                                  messages=messages,
                                  response_format=response_format,
                                  **model_params)
        except Timeout:
            # Grok have problem with stubborn not responding, after several moves, and retries are pointless
            if model.find("grok-4") != -1:
                return "Model not responding!"
            raise

        answer = response.choices[0].message.content
        logger.debug(answer)
        logger.debug(f"Request usage: {response['usage']}")

        self._add_tokens(model, response)

        return answer

    def _add_tokens(self, model: str, response: ModelResponse):

        try:
            model_usage = self.models_usage[model]
        except KeyError:
            model_usage = ModelUsage()
            self.models_usage[model] = model_usage

        usage = response.usage
        model_usage.prompt_tokens += usage.prompt_tokens
        completion_data = usage.completion_tokens_details
        if completion_data is not None:
            if completion_data.text_tokens is None:
                model_usage.text_tokens += 0
            else:
                model_usage.text_tokens += completion_data.text_tokens
            model_usage.reasoning_tokens += completion_data.reasoning_tokens
        else:
            model_usage.reasoning_tokens += usage.completion_tokens
        try:
            cost_float = completion_cost(response, model)
        except Exception:
            cost_float = 0
        cost_decimal = Decimal(cost_float)

        model_usage.total_cost_dollar += cost_decimal.quantize(Decimal("0.01"), rounding=ROUND_UP)

    @classmethod
    def get_usage(cls) -> ModelUsage:
        all_usage = ModelUsage()
        with threading.Lock():
            threads_usage = cls._threads_adapters.values()
            for thread_usage in threads_usage:
                models_usage = thread_usage.values()
                for model_usage in models_usage:
                    all_usage += model_usage
        return all_usage
