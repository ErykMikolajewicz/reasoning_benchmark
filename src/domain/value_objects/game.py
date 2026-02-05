from dataclasses import dataclass

from domain.enums import GameResult


@dataclass
class GameData:
    result: GameResult
    history: list[str]
    llm_color: bool
