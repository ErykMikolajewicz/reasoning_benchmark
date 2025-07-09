import numpy as np
from scipy.stats import bootstrap
import matplotlib.pyplot as plt

gemini_flash_2_5__benchmark_results = np.array([
    183.52, 286.3, 221.64, 193.16, 329.38, 279.11, 209.09, 211.85, 427.79, 397.85,
    308.85, 348.42, 425.36, 322.39, 317.82, 372.96, 404.4, 361.3, 391.64, 439.87,
    444.29, 421.25, 530.89, 558.79, 561.77, 431.4, 578.02, 589.9, 584.46, 572.43])

gemini_pro_2_5_benchmark_results = np.array([
    411.21, 271.04, 500.74, 474.56, 377.99, 410.77, 516.36, 555.98, 398.27, 446.19,
    474.42, 435.29, 481.61, 487.45, 521.67, 368.59, 579.84, 555.05, 562.18, 529.59,
    566.73, 815.63, 481.15, 738.17, 777.26, 753.39, 680.58, 427.78, 805.4, 754.0])

results = [
    ("Gemini Flash", gemini_flash_2_5__benchmark_results),
    ("Gemini Pro", gemini_pro_2_5_benchmark_results),
]

means, medians, mins, maxs, ci_lows, ci_highs = [], [], [], [], [], []

for _, data in results:
    means.append(np.mean(data))
    medians.append(np.median(data))
    mins.append(np.min(data))
    maxs.append(np.max(data))
    res = bootstrap(
        (data,),
        np.mean,
        vectorized=False,
        n_resamples=5000,
        method="BCa",
        confidence_level=0.95,
        random_state=42,
    )
    ci = res.confidence_interval
    ci_lows.append(ci.low)
    ci_highs.append(ci.high)

fig, ax = plt.subplots(figsize=(7, 7))

box = ax.boxplot([r[1] for r in results], vert=True, widths=0.6, patch_artist=True,
                 boxprops=dict(facecolor='lightblue'))

positions = [1, 2]
labels = [r[0] for r in results]

for i, pos in enumerate(positions):
    ax.scatter(pos, means[i], color="red", zorder=3)
    ax.vlines(pos, ci_lows[i], ci_highs[i], color="orange", linewidth=8, alpha=0.7)
    ax.fill_betweenx([ci_lows[i], ci_highs[i]], pos - 0.15, pos + 0.15, color="orange", alpha=0.15)

ax.set_xticks(positions)
ax.set_xticklabels(labels)
ax.set_ylabel('Wartość')
ax.set_title('Boxploty i przedziały ufności średniej (bootstrap BCa)')
ax.legend(
    [box["boxes"][0], ax.scatter([], [], color="red"), ax.vlines([], [], [], color="orange", linewidth=8)],
    ['Rozkład', 'Średnia', '95% CI (mean)'],
    loc='upper left'
)
plt.tight_layout()
plt.show()

for i, label in enumerate(labels):
    print(f"{label}:")
    print(f"  Mean:   {means[i]:.2f}")
    print(f"  Median: {medians[i]:.2f}")
    print(f"  Min:    {mins[i]:.2f}")
    print(f"  Max:    {maxs[i]:.2f}")
    print(f"  95% CI (mean): [{ci_lows[i]:.2f}, {ci_highs[i]:.2f}]")



