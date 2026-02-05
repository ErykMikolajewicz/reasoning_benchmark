import random
from itertools import cycle
from typing import Generator

from chess import BLACK, COLORS, WHITE, Color

from domain.enums import ColorGenerator
from share.settings.app import application_settings


def get_color_generator() -> Generator[Color, None, None]:
    match application_settings.COLOR_GENERATOR:
        case ColorGenerator.WHITE:
            color_generator = cycle((WHITE,))
        case ColorGenerator.BLACK:
            color_generator = cycle((BLACK,))
        case ColorGenerator.BOTH:
            color_generator = cycle(COLORS)
        case ColorGenerator.RANDOM:

            def color_generator():
                while True:
                    yield random.choice(COLORS)

        case _:
            raise Exception("Invalid config value!")

    return color_generator
