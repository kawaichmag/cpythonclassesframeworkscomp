import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Normalize for heatmap colors
from sklearn.preprocessing import MinMaxScaler

# Set style
plt.style.use("seaborn-v0_8-darkgrid")
sns.set_palette("husl")

# Read the CSV file
csv_file = "results/format_comparison.csv"
df = pd.read_csv(csv_file)

print("Format Comparison Results")
print("=" * 60)
print(df.to_string())

# Create figure with 4 subplots
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle(
    "Serialization Format Comparison (1 Million Objects)",
    fontsize=16,
    fontweight="bold",
)

# Colors for different formats
colors = plt.cm.Set3(np.linspace(0, 1, len(df)))

# 1. Serialization Time
ax1 = axes[0, 0]
bars1 = ax1.bar(df["format"], df["serialization_time"], color=colors, alpha=0.7)
ax1.set_xlabel("Format", fontsize=12)
ax1.set_ylabel("Time (seconds)", fontsize=12)
ax1.set_title("Serialization Time", fontsize=12, fontweight="bold")
ax1.grid(True, alpha=0.3, axis="y")
# Add value labels
for bar, val in zip(bars1, df["serialization_time"]):
    ax1.text(
        bar.get_x() + bar.get_width() / 2,
        val + 0.1,
        f"{val:.1f}s",
        ha="center",
        va="bottom",
        fontsize=9,
    )

# 2. Deserialization Time
ax2 = axes[0, 1]
bars2 = ax2.bar(df["format"], df["deserialization_time"], color=colors, alpha=0.7)
ax2.set_xlabel("Format", fontsize=12)
ax2.set_ylabel("Time (seconds)", fontsize=12)
ax2.set_title("Deserialization Time", fontsize=12, fontweight="bold")
ax2.grid(True, alpha=0.3, axis="y")
for bar, val in zip(bars2, df["deserialization_time"]):
    ax2.text(
        bar.get_x() + bar.get_width() / 2,
        val + 0.1,
        f"{val:.1f}s",
        ha="center",
        va="bottom",
        fontsize=9,
    )

# 3. Serialized Size
ax3 = axes[1, 0]
bars3 = ax3.bar(df["format"], df["serialized_size_mb"], color=colors, alpha=0.7)
ax3.set_xlabel("Format", fontsize=12)
ax3.set_ylabel("Size (MB)", fontsize=12)
ax3.set_title("Serialized Size", fontsize=12, fontweight="bold")
ax3.grid(True, alpha=0.3, axis="y")
for bar, val in zip(bars3, df["serialized_size_mb"]):
    ax3.text(
        bar.get_x() + bar.get_width() / 2,
        val + 1,
        f"{val:.0f}MB",
        ha="center",
        va="bottom",
        fontsize=9,
    )

# 4. Speed (MB/s)
ax4 = axes[1, 1]
bars4 = ax4.bar(df["format"], df["speed_mb_per_sec"], color=colors, alpha=0.7)
ax4.set_xlabel("Format", fontsize=12)
ax4.set_ylabel("Speed (MB/s)", fontsize=12)
ax4.set_title("Serialization Speed", fontsize=12, fontweight="bold")
ax4.grid(True, alpha=0.3, axis="y")
for bar, val in zip(bars4, df["speed_mb_per_sec"]):
    ax4.text(
        bar.get_x() + bar.get_width() / 2,
        val + 1,
        f"{val:.0f}MB/s",
        ha="center",
        va="bottom",
        fontsize=9,
    )

plt.tight_layout()
plt.savefig("results/format_comparison_plots.png", dpi=300, bbox_inches="tight")
plt.show()

# ============================================================================
# Create a radar chart for comparison (FIXED VERSION)
# ============================================================================
fig2, ax2 = plt.subplots(figsize=(10, 8), subplot_kw=dict(projection="polar"))
fig2.suptitle("Format Performance Radar Chart", fontsize=14, fontweight="bold")

# Define metrics (excluding speed for radar)
metrics = ["serialization_time", "deserialization_time", "serialized_size_mb"]
n_metrics = len(metrics)

# Normalize metrics (lower is better)
normalized = {}
for format_name in df["format"]:
    format_data = df[df["format"] == format_name]
    normalized[format_name] = []
    for metric in metrics:
        # Normalize (0 to 1, where 1 is best - meaning lowest value)
        min_val = df[metric].min()
        max_val = df[metric].max()
        if max_val > min_val:
            # For metrics where lower is better
            norm_val = 1 - (format_data[metric].values[0] - min_val) / (
                max_val - min_val
            )
        else:
            norm_val = 1
        normalized[format_name].append(norm_val)

    # Add speed separately if needed (higher is better)
    # But for radar, we'll keep it as separate or include in a different chart

# Create angles for each metric
angles = np.linspace(0, 2 * np.pi, n_metrics, endpoint=False).tolist()
angles += angles[:1]  # Close the loop

# Plot each format
for format_name, values in normalized.items():
    values_plot = values + values[:1]  # Close the loop
    ax2.plot(angles, values_plot, "o-", linewidth=2, label=format_name)
    ax2.fill(angles, values_plot, alpha=0.25)

# Set the ticks and labels
ax2.set_xticks(angles[:-1])
ax2.set_xticklabels(["Serialization Time", "Deserialization Time", "Size"])
ax2.set_ylim(0, 1)
ax2.set_ylabel("Performance Score (1 = best)", fontsize=10)
ax2.legend(loc="upper right", bbox_to_anchor=(1.3, 1.0))
ax2.grid(True)
plt.tight_layout()
plt.savefig("results/format_radar_chart.png", dpi=300, bbox_inches="tight")
plt.show()

# ============================================================================
# Create a grouped bar chart for all metrics
# ============================================================================
fig3, ax3 = plt.subplots(figsize=(12, 6))
fig3.suptitle(
    "Format Performance Comparison - All Metrics", fontsize=14, fontweight="bold"
)

# Normalize all metrics for comparison
metrics_to_plot = [
    "serialization_time",
    "deserialization_time",
    "serialized_size_mb",
    "speed_mb_per_sec",
]
normalized_df = df.copy()

for metric in metrics_to_plot:
    min_val = df[metric].min()
    max_val = df[metric].max()
    if metric == "speed_mb_per_sec":
        # For speed, higher is better
        if max_val > min_val:
            normalized_df[f"{metric}_norm"] = (df[metric] - min_val) / (
                max_val - min_val
            )
        else:
            normalized_df[f"{metric}_norm"] = 0.5
    else:
        # For time and size, lower is better
        if max_val > min_val:
            normalized_df[f"{metric}_norm"] = 1 - (df[metric] - min_val) / (
                max_val - min_val
            )
        else:
            normalized_df[f"{metric}_norm"] = 0.5

# Plot grouped bars
x = np.arange(len(df["format"]))
width = 0.2
multiplier = 0

for metric in metrics_to_plot:
    offset = width * multiplier
    bars = ax3.bar(
        x + offset, normalized_df[f"{metric}_norm"], width, label=metric, alpha=0.8
    )
    multiplier += 1

ax3.set_xlabel("Format", fontsize=12)
ax3.set_ylabel("Normalized Score (1 = best)", fontsize=12)
ax3.set_title("All Metrics Normalized Comparison", fontsize=12, fontweight="bold")
ax3.set_xticks(x + width * 1.5)
ax3.set_xticklabels(df["format"])
ax3.legend(loc="upper left", bbox_to_anchor=(1, 1))
ax3.set_ylim(0, 1.1)
ax3.grid(True, alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig("results/format_normalized_comparison.png", dpi=300, bbox_inches="tight")
plt.show()

# ============================================================================
# Create a heatmap of raw values
# ============================================================================
fig4, ax4 = plt.subplots(figsize=(10, 6))
heatmap_data = df.set_index("format")[
    [
        "serialization_time",
        "deserialization_time",
        "serialized_size_mb",
        "speed_mb_per_sec",
    ]
]

scaler = MinMaxScaler()
heatmap_normalized = pd.DataFrame(
    scaler.fit_transform(heatmap_data),
    index=heatmap_data.index,
    columns=heatmap_data.columns,
)

# For speed, invert the normalization (higher is better)
heatmap_normalized["speed_mb_per_sec"] = 1 - heatmap_normalized["speed_mb_per_sec"]

sns.heatmap(
    heatmap_normalized,
    annot=heatmap_data,
    fmt=".1f",
    cmap="RdYlGn_r",
    center=0.5,
    ax=ax4,
    cbar_kws={"label": "Performance (green = better)"},
)
ax4.set_title(
    "Format Performance Heatmap\n(Green = Better Performance)",
    fontsize=14,
    fontweight="bold",
)
plt.tight_layout()
plt.savefig("results/format_heatmap.png", dpi=300, bbox_inches="tight")
plt.show()

# ============================================================================
# Create a performance ranking table
# ============================================================================
print("\n" + "=" * 60)
print("PERFORMANCE RANKING (1 = best)")
print("=" * 60)

ranking_df = df.copy()
ranking_df["serialization_rank"] = ranking_df["serialization_time"].rank()
ranking_df["deserialization_rank"] = ranking_df["deserialization_time"].rank()
ranking_df["size_rank"] = ranking_df["serialized_size_mb"].rank()
ranking_df["speed_rank"] = ranking_df["speed_mb_per_sec"].rank(ascending=False)
ranking_df["overall_rank"] = (
    ranking_df["serialization_rank"]
    + ranking_df["deserialization_rank"]
    + ranking_df["size_rank"]
    + ranking_df["speed_rank"]
)

ranking_df = ranking_df.sort_values("overall_rank")
ranking_df["overall_rank"] = ranking_df["overall_rank"].rank()

print(
    ranking_df[
        [
            "format",
            "serialization_time",
            "deserialization_time",
            "serialized_size_mb",
            "speed_mb_per_sec",
            "overall_rank",
        ]
    ].to_string(index=False)
)

print("\n" + "=" * 60)
print("Plots saved to 'results' directory:")
print("  - format_comparison_plots.png (4-panel bar charts)")
print("  - format_radar_chart.png (radar chart for 3 metrics)")
print("  - format_normalized_comparison.png (grouped normalized bars)")
print("  - format_heatmap.png (performance heatmap)")
print("=" * 60)
