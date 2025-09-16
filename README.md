# LLM Reasoning Benchmark through Chess

This project is a benchmark designed to test the reasoning abilities of large language models (LLMs) using chess tasks.

---

## Why Chess?

Large language models such as **claude-opus-4.1** or **Gemini 2.5 Pro** still face significant challenges when playing chess. After the opening phase, which relies on known patterns, these models often make obvious mistakes—losing pieces without compensation or making illegal moves.

Chess is a particularly good test because:

- **Objective Evaluation**: The position on the board can be easily and objectively evaluated by a chess engine.
- **Demanding Tasks**: The benchmark is demanding and poses a real challenge for LLMs.

---

## How Does the Benchmark Work?

- The LLM plays a game against the weak **Stockfish engine**.
- When party is ended every move is evaluated.
- Moves in debut are discarded.
- The LLM score is calculated as the average of all positions scores.
- More about it in [methodology](docs/methodology.md)

## Flag models results

![Box plots and confident intervals](plots/results.png)

OpenAI model are currently the best. OpenAI o3 model - not seen on chart have slightly better performance, than gpt-5, but I decided to show more popular model.

Very good score in one party of deepseek reasoner is probably result of very poor move made by engine. Engine analysis depth is really shallow, what sometimes result in fatally bad moves.

## All results

| Model                              |   Mean | Median |    Min |    Max | Total cost ($) |
|:-----------------------------------|-------:|-------:|-------:|-------:|:---------------|
| real_human_elo_1700                |   2.16 |   2.16 |   0.49 |   3.82 | -              |
| real_human_me                      |   1.09 |   0.93 |  -1.01 |   4.04 | -              |
| openai-o3                          |  -1.46 |  -0.44 |  -5.91 |   1.63 | 10.52          |
| openai-gpt-5                       |  -3.59 |  -1.59 | -22.11 |   5.42 | 11.81          |
| openai-o4-mini                     |  -7.74 |   -5.0 | -19.22 |  -0.72 | 6.38           |
| anthropic-claude-opus-4-1-20250805 | -14.89 | -14.67 | -29.47 |  -4.89 | 8.86           |
| anthropic-claude-sonnet-4-20250514 | -21.01 | -20.03 | -29.67 | -10.87 | 3.78           |
| deepseek-deepseek-reasoner         | -16.98 | -24.16 |  -32.0 |  24.36 | 1.46           |
| gemini-gemini-2.5-pro              | -24.19 | -25.52 |  -32.0 | -11.53 | 1.60           |
| xai-grok-code-fast-1               | -27.63 | -30.19 |  -32.0 | -17.24 | 0.54           |
| gemini-gemini-2.5-flash            | -30.56 | -31.35 |  -32.0 | -28.03 | 0.43           |

All results, with parties record are available under:
https://drive.google.com/drive/folders/1a3sqEMmo99rRIoFuM6GCEfgdtU7WkDsl?usp=drive_link

## Humans versus best models

![](plots/best_vs_humans.png)

- As you can see humans with some chess experience are currently still better than large language models.
- Number of plays for human with elo 1700 is unfortunately low, only 2 parties.
- I do not have any official elo. I had been playing for 5 years, once a week as a teenager. I obtained the 3rd Polish chess category, roughly equivalent to an Elo rating of 1500.

---

## Run in cloud
You can execute benchmark in your local computer, but sometimes it use quite a lot of time due to reasoning time, or model rate limits.
It is possible to run benchmark in cloud, [check it](docs/cloud_run.md)

## Roadmap

Planned next steps for the project include:

1. **Add examples of Grok play**
   Currently Grok unexpectedly timeout during every play, at lite moves. it can be problem with model itself or litellm.

2. **Batch API Support**  
   Implement support for batch API operations, making it possible to submit and process multiple games or tasks simultaneously.

3. **Implement More Chess Strategies for LLM**
   Expand the set of prompts used to interact with the LLM, allowing assessment of how different instructions or phrasings affect performance and reasoning in chess tasks.
