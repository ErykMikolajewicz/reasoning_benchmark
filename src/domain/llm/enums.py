from enum import StrEnum


class LlmStrategy(StrEnum):
    DEFAULT = "DEFAULT"
    SIMPLE_MOVE = "SIMPLE_MOVE"
    HUMAN_PLAY = "HUMAN_PLAY"
    MAINTAIN_STRATEGY = "MAINTAIN_STRATEGY"
