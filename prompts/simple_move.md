# Chess Move Agent Instructions

You are playing chess. Your task is to win a game.
To do it try to make the best move in current position.

## Move info
1. Spend some time to validating that your move is consistent with chess rules. Invalid move will lose a party
2. Write a move in algebraic notation, example move: `Rh3`

## Board:
{{ ascii_board }}

Castling rights: {{ castling_rights }}.

Last opponent move: {{ last_opponent_move }}.

You are {{ llm_color }}.