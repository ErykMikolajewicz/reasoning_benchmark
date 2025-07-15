from pathlib import Path
import json

import numpy as np
from scipy.stats import bootstrap
import matplotlib.pyplot as plt

results_dir = Path("results")

json_files = results_dir.glob("*.json")

results = {}

for filepath in json_files:
    with open(filepath, 'r', encoding='utf-8') as benchmark_file:
        benchmark_result = json.load(benchmark_file)
    model_name = benchmark_result['model_name']
    scores = benchmark_result['scores']
    scores = np.array(scores, dtype=float)
    results[model_name] = {'scores': scores}

for benchmark_data in results.values():
    scores = benchmark_data['scores']
    if len(scores) < 2:
        raise ValueError('Not enough scores to make an analyze!')

    benchmark_data['mean'] = np.mean(scores)
    benchmark_data['median'] = np.median(scores)
    benchmark_data['min'] = np.min(scores)
    benchmark_data['max'] = np.max(scores)

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
    benchmark_data['ci_low'] = ci.low
    benchmark_data['ci_high'] = ci.high

fig, ax = plt.subplots()

box = ax.boxplot([r['scores'] for r in results.values()], vert=True, widths=0.6, patch_artist=True,
                 boxprops=dict(facecolor='lightblue'))

for i, benchmark_data in enumerate(results.values(), start = 1):
    ax.scatter(i, benchmark_data['mean'], color="red", zorder=3)
    ax.vlines(i, benchmark_data['ci_low'], benchmark_data['ci_high'], linewidth=8, alpha=0.7)
    ax.fill_betweenx([benchmark_data['ci_low'], benchmark_data['ci_high']], i - 0.15, i + 0.15, alpha=0.15)

positions = list(range(1, len(results) + 1))

ax.set_xticks(positions)
ax.set_xticklabels(results.keys(), rotation=15)
ax.set_ylabel('Values')
ax.set_title('Box plots and confident intervals (bootstrap BCa)')
ax.legend(
    [box["boxes"][0], ax.scatter([], [], color="red"), ax.vlines([], [], [], linewidth=8)],
    ['Distribution', 'Average', '95% CI (mean)'],
    loc='upper left'
)
plt.tight_layout()
plt.show()

for label, benchmark_data in results.items():
    print(f"{label}:")
    print(f"  Mean:   {benchmark_data['mean']:.2f}")
    print(f"  Median: {benchmark_data['median']:.2f}")
    print(f"  Min:    {benchmark_data['min']:.2f}")
    print(f"  Max:    {benchmark_data['max']:.2f}")
    print(f"  95% CI (mean): [{benchmark_data['ci_low']:.2f}, {benchmark_data['ci_high']:.2f}]")
