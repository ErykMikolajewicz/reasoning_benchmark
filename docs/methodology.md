# Benchmark Methodology

The benchmark is based on a language model playing chess against the **Stockfish** engine.  
After each game, the position is evaluated move by move — typically by another instance of the engine with higher analysis depth settings.  

To avoid scoring mechanical replay of opening theory (instead of genuine play), part of the initial moves is discarded.  
After the game ends, all subsequent moves up to the maximum number of moves are assigned a score consistent with the game outcome.  
Finally, the average of all evaluations is calculated.

### Moves scale after end game:
- **Win** – maximum engine score: `+32 pawns`  
- **Loss** – minimum engine score: `-32 pawns`  
- **Draw** – `0 pawns` (evaluation of an equal position)

Ale important settings are attached to benchmark result files.

---

# Engine Configuration

The engine is currently set to **low playing strength** so that it does not pose an excessive challenge to language models.  
Configuration parameters:

- **ANALYSE_DEPTH** – controls the engine strength.
- **MULTI_PV** – forces selection among multiple options to introduce variability in games.  
- **MOVE_ACCEPTANCE_THRESHOLD_CENTI_PAWS** – the minimum level of acceptable moves compared to the best one. Thanks to this, extremely poor moves are rejected (e.g., when in check, the engine will not choose a move leading to immediate loss).

Engine settings can be set in the file:  
`settings/engine.env`

---

# Benchmark Settings

The benchmark has three main parameters:

1. **MAX_MOVES** – maximum game length  
   - Primarily regulates benchmark costs.  
   - Also affects the result: every move is scored, and the outcome is better if a win occurs earlier or a loss occurs later.  

2. [**STRATEGIES**](strategies.md) – playing strategy  
   - Defined by a set of prompts. 
   - Decide what information llm get to make its tasks

3. **MAX_ILLEGAL_MOVES** – tolerance for model errors.  

Benchmark settings can be set in the file:  
`settings/benchmark.env`

---

# Additional LLM Configuration

It is possible to configure additional parameters of language models, such as:

- **temperature**  
- **reasoning_effort**

To do this, add a file with the provider and model name into the folder:  
`models_params`  
(a hyphen `-` must be used instead of a slash `/` in the file name).

For some models, a **maximum reasoning budget** has been set to avoid problems with missing responses or timeouts.
