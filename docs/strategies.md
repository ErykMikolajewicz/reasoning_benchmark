# Strategies

Strategies consist of prompts that instruct the language model on how to perform its tasks. They can also influence the scope of data passed to the model.

---

## Simple Move

The simplest strategy, consisting of information about the current situation on the board. It includes not only the placement of pieces, but also information about castling rights and the opponent's previous move, which is important for determining the right to en passant. It also encourages checking the validity of a move, as mistakes here are frequent and costly.

**Example prompt view:**

```
System:
You will be playing chess. Each time, you will receive a text representation of the board. You will also be informed which color you are playing.
Your task will be to make a move. Spend some time to validate if your move is consistent with the rules of chess.
Return answer in algebraic notation, in json, example:
{"move":"Rh3"}

User:
Board:
r n b q k b n r
p p p . . p p p
. . . . . . . .
. . . p p . . .
. . . . P . . .
. . . . . N . .
P P P P . P P P
R N B Q K B . R

Castling rights: KQkq.
Last opponent move: d5.
You are white.
```

---

## Strategy Maintenance

A slightly more complex strategy, in which the language model can pass a note containing the strategy between moves. The strategy should be fairly general, with the goal of increasing long-term consistency of play, as well as saving information since the language model does not need to repeatedly arrive at the same conclusions.

**Example prompt view:**

```
System:
You will be playing chess. Each time, you will receive a text representation of the board. You will also be informed which color you are playing.
Your task will be to make a move. Spend some time to validate if your move is consistent with the rules of chess.
After the first move you will also get a strategy. The strategy is written by you, used to maintain relevant information between turns.
Spend some time to analyze if your strategy is still relevant, and make necessary corrections. Then write your move.
A strategy should be rather general and aimed at allowing you to maintain a consistent style of play during the game, or to carry out longer-term plans.
Return strategy and move in algebraic notation, in json, example:
{"strategy": "I'm playing the Sicilian Defense. My plan is to attack with pawns on the queenside and, where possible, place my knights well in the centre; furthermore...", 
"move":"Rh3"}

User:
Board:
r n b q k b . r
p p . . p p p p
. . . p . n . .
. . p . . . . .
. . . . P . . .
. . N . . N . .
P P P P . P P P
R . B Q K B . R

Castling rights: KQkq.
Last opponent move: c5.
You are white.
Your strategy:
My primary goal is to control the center of the board, particularly the e4 and d4 squares. I will develop my minor pieces (Knights and Bishops) efficiently, aiming to castle kingside early for king safety and to connect my rooks. I will avoid premature queen moves and look for opportunities to create pawn breaks to open lines for my pieces. The previous move Nc3 aligned with defending the e4 pawn and developing a minor piece to a central square. The current move Nf3 continues this plan by developing another knight, controlling central squares, and preparing for kingside castling.
```

---

## Comparisons

Results of comparing the simple move and hold strategies for two promising language models.

| Model                      |   Mean | Median |    Min |   Max | Total cost ($) |
|:---------------------------|-------:|-------:|-------:|------:|:---------------|
| o3_maintain_strategy       |  -1.12 |   0.46 | -16.62 |  5.43 | 9.40           |
| o3_simple_move             |  -1.43 |  -0.44 |  -5.73 |  1.61 | 10.52          |
| opus-4.1_simple_move       | -14.88 | -14.67 | -29.47 | -4.87 | 8.86           |
| opus-4.1_maintain_strategy | -15.32 | -17.21 | -22.26 | -1.66 | 7.98           |


As we can see, in the case of the opus-4.1 model, the attempt to maintain a long-term strategy caused a significant deterioration in the model's results.
The situation is different for the o3 model, which demonstrated an improvement in effectiveness, measured by the median of 1 pawn.
It is also worth noting the more than 10% reduction in benchmark cost.

The game record along with the strategy for the o3 model can be found in `logs/maintain_strategy_o3_logs.json`
