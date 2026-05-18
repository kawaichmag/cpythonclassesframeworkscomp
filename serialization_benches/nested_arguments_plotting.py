import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Set style for better looking plots
plt.style.use("seaborn-v0_8-darkgrid")
sns.set_palette("husl")

# Create results directory if it doesn't exist
Path("results").mkdir(exist_ok=True)

# Read the CSV file
csv_file = "results/nested_serialization.csv"
df = pd.read_csv(csv_file)

print("Nested Object Benchmark Results")
print("=" * 60)
print(f"Data shape: {df.shape}")
print(f"Depth range: {df['depth'].min()} to {df['depth'].max()}")
print("\nSummary statistics by module:")
print(
    df.groupby("m_name")
    .agg(
        {
            "t_creation": "mean",
            "t_serialization": "mean",
            "t_deserialization": "mean",
            "mem": "mean",
            "serialized_size": "mean",
        }
    )
    .round(3)
)

# Colors for different modules
colors = {"msgspec": "#2ecc71", "pydantic": "#e74c3c", "dataclass": "#3498bd"}
markers = {"msgspec": "o", "pydantic": "s", "dataclass": "^"}

# ============================================================================
# Figure 1: Main 4-panel comparison (Creation, Serialization, Deserialization, Memory)
# ============================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle(
    "Nested Object Serialization Benchmark: Depth Performance",
    fontsize=16,
    fontweight="bold",
)

# 1. Creation Time
ax1 = axes[0, 0]
for module in df["m_name"].unique():
    module_data = df[df["m_name"] == module]
    ax1.plot(
        module_data["depth"],
        module_data["t_creation"],
        label=module,
        linewidth=2,
        marker=markers[module],
        markersize=4,
        color=colors[module],
    )
ax1.set_xlabel("Nesting Depth", fontsize=12)
ax1.set_ylabel("Creation Time (seconds)", fontsize=12)
ax1.set_title("Object Creation Time by Nesting Depth", fontsize=12, fontweight="bold")
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_xscale("log")
ax1.set_yscale("log")
ax1.set_xlim(left=0.9)

# 2. Serialization Time
ax2 = axes[0, 1]
for module in df["m_name"].unique():
    module_data = df[df["m_name"] == module]
    ax2.plot(
        module_data["depth"],
        module_data["t_serialization"],
        label=module,
        linewidth=2,
        marker=markers[module],
        markersize=4,
        color=colors[module],
    )
ax2.set_xlabel("Nesting Depth", fontsize=12)
ax2.set_ylabel("Serialization Time (seconds)", fontsize=12)
ax2.set_title("Serialization Time by Nesting Depth", fontsize=12, fontweight="bold")
ax2.legend()
ax2.grid(True, alpha=0.3)
ax2.set_xscale("log")
ax2.set_yscale("log")
ax2.set_xlim(left=0.9)

# 3. Deserialization Time
ax3 = axes[1, 0]
for module in df["m_name"].unique():
    module_data = df[df["m_name"] == module]
    ax3.plot(
        module_data["depth"],
        module_data["t_deserialization"],
        label=module,
        linewidth=2,
        marker=markers[module],
        markersize=4,
        color=colors[module],
    )
ax3.set_xlabel("Nesting Depth", fontsize=12)
ax3.set_ylabel("Deserialization Time (seconds)", fontsize=12)
ax3.set_title("Deserialization Time by Nesting Depth", fontsize=12, fontweight="bold")
ax3.legend()
ax3.grid(True, alpha=0.3)
ax3.set_xscale("log")
ax3.set_yscale("log")
ax3.set_xlim(left=0.9)

# 4. Memory Consumption
ax4 = axes[1, 1]
for module in df["m_name"].unique():
    module_data = df[df["m_name"] == module]
    ax4.plot(
        module_data["depth"],
        module_data["mem"],
        label=module,
        linewidth=2,
        marker=markers[module],
        markersize=4,
        color=colors[module],
    )
ax4.set_xlabel("Nesting Depth", fontsize=12)
ax4.set_ylabel("Memory Usage (MB)", fontsize=12)
ax4.set_title("Memory Consumption by Nesting Depth", fontsize=12, fontweight="bold")
ax4.legend()
ax4.grid(True, alpha=0.3)
ax4.set_xscale("log")
ax4.set_yscale("log")
ax4.set_xlim(left=0.9)

plt.tight_layout()
plt.savefig("results/nested_benchmark_plots.png", dpi=300, bbox_inches="tight")
plt.show()

# ============================================================================
# Figure 2: Serialized Size Growth
# ============================================================================
fig2, ax = plt.subplots(figsize=(10, 6))
for module in df["m_name"].unique():
    module_data = df[df["m_name"] == module]
    ax.plot(
        module_data["depth"],
        module_data["serialized_size"],
        label=module,
        linewidth=2,
        marker=markers[module],
        markersize=5,
        color=colors[module],
    )
ax.set_xlabel("Nesting Depth", fontsize=12)
ax.set_ylabel("Serialized Size (MB)", fontsize=12)
ax.set_title(
    "Serialized Size Growth with Nesting Depth", fontsize=14, fontweight="bold"
)
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(left=0.9)
plt.tight_layout()
plt.savefig("results/nested_size_growth.png", dpi=300, bbox_inches="tight")
plt.show()

# ============================================================================
# Figure 3: Bar comparison at specific depths
# ============================================================================
depths_to_show = [1, 5, 10, 25, 50, 100]
fig3, axes3 = plt.subplots(2, 3, figsize=(15, 8))
fig3.suptitle(
    "Performance Comparison at Different Nesting Depths", fontsize=14, fontweight="bold"
)
axes3_flat = axes3.flatten()

for idx, depth in enumerate(depths_to_show):
    if depth <= df["depth"].max():
        ax = axes3_flat[idx]
        subset = df[df["depth"] == depth]

        if not subset.empty:
            x_pos = np.arange(len(subset))
            width = 0.25

            bars1 = ax.bar(
                x_pos - width,
                subset["t_creation"],
                width,
                label="Creation",
                alpha=0.8,
                color="#3498db",
            )
            bars2 = ax.bar(
                x_pos,
                subset["t_serialization"],
                width,
                label="Serialization",
                alpha=0.8,
                color="#e74c3c",
            )
            bars3 = ax.bar(
                x_pos + width,
                subset["t_deserialization"],
                width,
                label="Deserialization",
                alpha=0.8,
                color="#2ecc71",
            )

            ax.set_xlabel("Module")
            ax.set_ylabel("Time (seconds)")
            ax.set_title(f"Depth = {depth}")
            ax.set_xticks(x_pos)
            ax.set_xticklabels(subset["m_name"])
            ax.legend()
            ax.grid(True, alpha=0.3)

            # Add value labels on bars
            for bars in [bars1, bars2, bars3]:
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:
                        ax.text(
                            bar.get_x() + bar.get_width() / 2.0,
                            height,
                            f"{height:.2f}",
                            ha="center",
                            va="bottom",
                            fontsize=8,
                        )

# Hide any unused subplots
for idx in range(len(depths_to_show), len(axes3_flat)):
    axes3_flat[idx].set_visible(False)

plt.tight_layout()
plt.savefig("results/nested_bar_comparison.png", dpi=300, bbox_inches="tight")
plt.show()

# ============================================================================
# Figure 4: Time per depth level (efficiency)
# ============================================================================
fig4, axes4 = plt.subplots(1, 3, figsize=(15, 5))
fig4.suptitle(
    "Efficiency Analysis: Time per Nesting Level", fontsize=14, fontweight="bold"
)

metrics = [
    ("t_creation", "Creation Time per Level", "#3498db"),
    ("t_serialization", "Serialization Time per Level", "#e74c3c"),
    ("t_deserialization", "Deserialization Time per Level", "#2ecc71"),
]

for idx, (metric, title, color) in enumerate(metrics):
    ax = axes4[idx]
    for module in df["m_name"].unique():
        module_data = df[df["m_name"] == module].copy()
        # Calculate time per depth level
        module_data["time_per_level"] = module_data[metric] / module_data["depth"]
        ax.plot(
            module_data["depth"],
            module_data["time_per_level"],
            label=module,
            linewidth=2,
            marker=markers[module],
            markersize=4,
            color=colors[module],
        )
    ax.set_xlabel("Nesting Depth", fontsize=11)
    ax.set_ylabel("Time per Level (seconds)", fontsize=11)
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(left=0.9)

plt.tight_layout()
plt.savefig("results/nested_efficiency_analysis.png", dpi=300, bbox_inches="tight")
plt.show()

# ============================================================================
# Figure 5: Memory efficiency (memory per object)
# ============================================================================
fig5, ax = plt.subplots(figsize=(10, 6))
OBJECTS_PER_STEP = 1000  # From the benchmark script
for module in df["m_name"].unique():
    module_data = df[df["m_name"] == module].copy()
    # Calculate memory per object in KB
    module_data["mem_per_object"] = (module_data["mem"] * 1024) / OBJECTS_PER_STEP
    ax.plot(
        module_data["depth"],
        module_data["mem_per_object"],
        label=module,
        linewidth=2,
        marker=markers[module],
        markersize=5,
        color=colors[module],
    )
ax.set_xlabel("Nesting Depth", fontsize=12)
ax.set_ylabel("Memory per Object (KB)", fontsize=12)
ax.set_title(
    "Memory Efficiency: Average Memory per Object", fontsize=14, fontweight="bold"
)
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(left=0.9)
plt.tight_layout()
plt.savefig("results/nested_memory_efficiency.png", dpi=300, bbox_inches="tight")
plt.show()

# ============================================================================
# Figure 6: Correlation heatmap
# ============================================================================
fig6, ax = plt.subplots(figsize=(10, 8))
correlation_data = df[
    [
        "depth",
        "t_creation",
        "t_serialization",
        "t_deserialization",
        "mem",
        "serialized_size",
    ]
].copy()
correlation_matrix = correlation_data.corr()

# Create mask for upper triangle
mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))

sns.heatmap(
    correlation_matrix,
    annot=True,
    cmap="coolwarm",
    center=0,
    ax=ax,
    fmt=".2f",
    square=True,
    linewidths=1,
    mask=mask,
)
ax.set_title("Correlation Between Metrics", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("results/nested_correlation_heatmap.png", dpi=300, bbox_inches="tight")
plt.show()

# ============================================================================
# Print performance analysis
# ============================================================================
print("\n" + "=" * 60)
print("PERFORMANCE ANALYSIS (pydantic & dataclass relative to msgspec)")
print("=" * 60)

for metric in [
    "t_creation",
    "t_serialization",
    "t_deserialization",
    "mem",
    "serialized_size",
]:
    print(f"\n{metric.upper()} RATIOS:")
    msgspec_avg = df[df["m_name"] == "msgspec"][metric].mean()
    pydantic_avg = df[df["m_name"] == "pydantic"][metric].mean()
    dataclass_avg = df[df["m_name"] == "dataclass"][metric].mean()

    print(f"  pydantic/msgspec: {pydantic_avg / msgspec_avg:.2f}x")
    print(f"  dataclass/msgspec: {dataclass_avg / msgspec_avg:.2f}x")

# Find scaling behavior (linear, quadratic, exponential)
print("\n" + "=" * 60)
print("SCALING BEHAVIOR ANALYSIS")
print("=" * 60)

for module in df["m_name"].unique():
    print(f"\n{module.upper()}:")
    module_data = df[df["m_name"] == module]

    # Calculate approximate scaling exponents using log-log regression
    for metric in [
        "t_creation",
        "t_serialization",
        "t_deserialization",
        "mem",
        "serialized_size",
    ]:
        if len(module_data) > 1:
            log_depth = np.log(module_data["depth"])
            log_metric = np.log(module_data[metric])

            # Simple linear regression on log-log
            slope, intercept = np.polyfit(log_depth, log_metric, 1)

            if slope < 1.1:
                scaling = "sub-linear"
            elif slope < 1.9:
                scaling = "near-linear"
            elif slope < 2.1:
                scaling = "quadratic"
            else:
                scaling = f"super-quadratic (^{slope:.2f})"

            print(f"  {metric}: O(n^{slope:.2f}) - {scaling}")

print("\n" + "=" * 60)
print("All plots saved to 'results' directory:")
print("  - nested_benchmark_plots.png (4-panel comparison)")
print("  - nested_size_growth.png (serialized size growth)")
print("  - nested_bar_comparison.png (bar chart at specific depths)")
print("  - nested_efficiency_analysis.png (time per nesting level)")
print("  - nested_memory_efficiency.png (memory per object)")
print("  - nested_correlation_heatmap.png (correlation analysis)")
print("=" * 60)
