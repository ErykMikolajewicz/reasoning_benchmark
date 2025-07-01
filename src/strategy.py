import json
import os

from chess import Color, Board

from src.models_adapter import send_messages
from src.prompts import main_prompt, extraction_prompt

BENCHMARKING_MODEL = os.environ["BENCHMARKING_MODEL"]
EXTRACTION_MODEL = os.environ["EXTRACTION_MODEL"]
color_to_string = lambda color: {True: "white", False: "black"}[color]


def llm_move(board: Board, color: Color):
    color_string = color_to_string(color)
    ascii_board = str(board)
    board_prompt = f"Board:/n{ascii_board}\nYou are {color_string}"
    response = send_messages(
        model=BENCHMARKING_MODEL,
        messages=[{"role": "system", "content": main_prompt},
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
    move = move_json['san']

    return move
