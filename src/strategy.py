import json

from chess import Board, Color

from src.models_adapter import send_messages
from src.prompts import move_prompt, extraction_prompt, move_formated
from src.helpers import color_to_string
from src.settings import settings

BENCHMARKING_MODEL = settings.benchmark.BENCHMARKING_MODEL
EXTRACTION_MODEL = settings.benchmark.EXTRACTION_MODEL


def simple_move(board: Board, color: Color):
    color_string = color_to_string(color)
    ascii_board = str(board)
    board_prompt = f"Board:/n{ascii_board}\nYou are {color_string}"
    move_and_thinking = send_messages(
        model=BENCHMARKING_MODEL,
        messages=[{"role": "system", "content": move_formated},
                  {"role": "user", "content": board_prompt}]
    )

    json_start_index = move_and_thinking.index('{')
    json_end_index = move_and_thinking.rindex('}')
    only_move = move_and_thinking[json_start_index:json_end_index + 1]
    move_json = json.loads(only_move)
    move = move_json['move']

    return move


def move_and_extract(board: Board, color: Color):
    color_string = color_to_string(color)
    ascii_board = str(board)
    board_prompt = f"Board:/n{ascii_board}\nYou are {color_string}"
    response = send_messages(
        model=BENCHMARKING_MODEL,
        messages=[{"role": "system", "content": move_prompt},
                  {"role": "user", "content": board_prompt}]
    )

    move_and_thinking: str = response

    response = send_messages(
        model=EXTRACTION_MODEL,
        messages=[{"role": "system", "content": extraction_prompt},
                  {"role": "user", "content": move_and_thinking}]
    )

    move_str: str = response
    json_start_index = move_str.index('{')
    json_end_index = move_str.rindex('}')
    move_json = json.loads(move_str[json_start_index:json_end_index + 1])
    move = move_json['move']

    return move


strategies = {
    None: simple_move,
    'simple_move': simple_move,
    'move_and_extract': move_and_extract
}
