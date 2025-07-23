board_prompt = """
Board:
{ascii_board}

Castling rights: {castling_rights}.
Last opponent move: {last_opponent_move}.
You are {llm_color}."""

move_prompt = """
You will be playing chess. Each time, you will receive a text representation of board. You will also be informed which color you are playing.
Your task will be to make a move. Spend some time to validate is your move consistent with the rules of chess."""

move_formated = (
    move_prompt
    + """\nReturn answer in algebraic notation, in json, example:
{"move":"Rh3"}"""
)

EXTRACTION_PROMPT = """
Extract user move from text, and return it in algebraic notation format, in json, example:
{"move":"Rh3"}"""
