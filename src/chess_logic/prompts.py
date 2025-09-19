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

strategy_prompt = """
After first move you will also get a strategy. The strategy is written by you text, used to maintain relevant information between turns.
Spend some time to analyze is your strategy still actual, and make necessary corrections. Then write your move.
A strategy should be rather general and aimed at allowing you to maintain a consistent style of play during the game, or to carry out longer-term plans.
Return strategy and move in algebraic notation, in json, example:
{"strategy": "I'm playing the Sicilian Defense. My plan is to attack with pawns on the queenside and, where possible, place my knights well in the centre; furthermore...", 
"move":"Rh3"}"""

move_with_strategy = move_prompt + strategy_prompt
