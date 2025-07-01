# LLM Reasoning Benchmark through Chess

This project is a benchmark designed to test the reasoning abilities of large language models (LLMs) using chess tasks.

---

## Why Chess?

Large language models such as **GPT-4.1** or **Gemini 2.5 Pro** still face significant challenges when playing chess. After the opening phase, which relies on known patterns, these models often make obvious mistakes—losing pieces without compensation or making illegal moves.

Chess is a particularly good test because:

- **Objective Evaluation**: The position on the board can be easily and objectively evaluated by a chess engine.
- **Demanding Tasks**: The benchmark is demanding and poses a real challenge for LLMs.

---

## How Does the Benchmark Work?

- The LLM plays a game against the **Stockfish engine** (with search depth limited to **1 ply**, i.e., depth=1), making Stockfish play very weakly.
- This prevents the LLM from being immediately outclassed and allows meaningful differentiation between results.
- After **30 moves**, the chess engine evaluates the board position.  
- The better the position achieved by the LLM, the stronger its reasoning and planning capabilities.

---

## Challenges

- **Achieving a Long Series of Correct Moves**  
  Currently, language models often hallucinate illegal or incorrect moves.
- **High Variability of Results**  
  Benchmark outcomes can vary greatly depending on how the opening unfolds.
