import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import bootstrap

import src.metrics.scoring as scoring
from src.utils.helpers import get_model_shorter_name

results_dir = Path("results")

json_files = results_dir.glob("*.json")

results = {}

for filepath in json_files:
    with open(filepath, "r", encoding="utf-8") as benchmark_file:
        benchmark_result = json.load(benchmark_file)
    model_name = benchmark_result["model_name"]
    games_data = benchmark_result["games_data"]
    games_score = []
    for game_data in games_data:
        llm_color = game_data["llm_color"]
        game_history = game_data["history"]
        game_result = game_data["result"]
        position_scores = scoring.score_positions(game_history, llm_color)
        game_score = scoring.get_game_score(position_scores, game_result)
        games_score.append(game_score)
    scores = np.array(games_score, dtype=float)
    results[model_name] = {"scores": scores}
scoring.engine.quit()

for benchmark_data in results.values():
    scores = benchmark_data["scores"]
    if len(scores) < 2:
        raise ValueError("Not enough scores to make an analyze!")

    benchmark_data["mean"] = np.mean(scores)
    benchmark_data["median"] = np.median(scores)
    benchmark_data["min"] = np.min(scores)
    benchmark_data["max"] = np.max(scores)

    res = bootstrap(
        [scores],
        np.mean,
        vectorized=False,
        n_resamples=5000,
        method="BCa",
        confidence_level=0.95,
        random_state=42,
    )
    ci = res.confidence_interval
    benchmark_data["ci_low"] = ci.low
    benchmark_data["ci_high"] = ci.high

fig, ax = plt.subplots()

box = ax.boxplot(
    [r["scores"] for r in results.values()],
    vert=False,
    widths=0.6,
    patch_artist=True,
    boxprops=dict(facecolor="lightblue"),
)

positions = list(range(1, len(results) + 1))

for i, benchmark_data in enumerate(results.values(), start=1):
    ax.scatter(benchmark_data["mean"], i, color="red", zorder=3)
    ax.hlines(i, benchmark_data["ci_low"], benchmark_data["ci_high"], linewidth=8, alpha=0.7)
    ax.fill_between([benchmark_data["ci_low"], benchmark_data["ci_high"]], i - 0.15, i + 0.15, alpha=0.15)

ax.set_yticks(positions)
ax.set_yticklabels(get_model_shorter_name(key) for key in results.keys())
ax.set_xlabel("Values")
ax.set_title("Box plots and confident intervals (bootstrap BCa)")

ax.legend(
    [box["boxes"][0], ax.scatter([], [], color="red"), ax.hlines([], [], [], linewidth=8)],
    ["Distribution", "Average", "95% CI (mean)"],
    loc="center left",
    bbox_to_anchor=(1, 0.5),
)
plt.tight_layout()
plt.show()

for label, benchmark_data in sorted(results.items(), key=lambda x: x[1]["median"], reverse=True):
    print(f"{label}:")
    print(f"  Mean:   {benchmark_data['mean']:.2f}")
    print(f"  Median: {benchmark_data['median']:.2f}")
    print(f"  Min:    {benchmark_data['min']:.2f}")
    print(f"  Max:    {benchmark_data['max']:.2f}")
    print(f"  95% CI (mean): [{benchmark_data['ci_low']:.2f}, {benchmark_data['ci_high']:.2f}]")
