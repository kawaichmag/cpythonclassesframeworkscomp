import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style for better looking plots
plt.style.use("seaborn-v0_8-darkgrid")
sns.set_palette("husl")

# Read the CSV file
csv_file = "results/continuous_serialization.csv"
df = pd.read_csv(csv_file)

# Display basic info about the data
print("Data loaded successfully!")
print(f"Shape: {df.shape}")
print("\nFirst few rows:")
print(df.head())
print("\nBasic statistics:")
print(df.describe())

# Create figure with 3 subplots
fig, axes = plt.subplots(3, 1, figsize=(12, 15))
fig.suptitle(
    "Serialization Benchmark: msgspec vs pydantic vs dataclass",
    fontsize=16,
    fontweight="bold",
)

# Colors for different modules
colors = {"msgspec": "#2ecc71", "pydantic": "#e74c3c", "dataclass": "#3498db"}

# 1. Memory Consumption subplot
ax1 = axes[0]
for module in df["m_name"].unique():
    module_data = df[df["m_name"] == module]
    ax1.plot(
        module_data["n_args"],
        module_data["mem"],
        label=module,
        linewidth=2,
        marker="o",
        markersize=3,
        color=colors[module],
    )
ax1.set_xlabel("Number of Atributes", fontsize=12)
ax1.set_ylabel("Memory Usage (MB)", fontsize=12)
ax1.set_title(
    "Memory Consumption by Number of Atributes", fontsize=14, fontweight="bold"
)
ax1.legend(loc="upper left")
ax1.grid(True, alpha=0.3)
ax1.set_xscale("log")
ax1.set_yscale("log")
ax1.set_xlim(left=0.9)

# 2. Creation Time subplot
ax2 = axes[1]
for module in df["m_name"].unique():
    module_data = df[df["m_name"] == module]
    ax2.plot(
        module_data["n_args"],
        module_data["t_creation"],
        label=module,
        linewidth=2,
        marker="s",
        markersize=3,
        color=colors[module],
    )
ax2.set_xlabel("Number of Atributes", fontsize=12)
ax2.set_ylabel("Creation Time (seconds)", fontsize=12)
ax2.set_title(
    "Object Creation Time by Number of Atributes", fontsize=14, fontweight="bold"
)
ax2.legend(loc="upper left")
ax2.grid(True, alpha=0.3)
ax2.set_xscale("log")
ax2.set_yscale("log")
ax2.set_xlim(left=0.9)

# 3. Serialization Time subplot
ax3 = axes[2]
for module in df["m_name"].unique():
    module_data = df[df["m_name"] == module]
    ax3.plot(
        module_data["n_args"],
        module_data["t_serialization"],
        label=module,
        linewidth=2,
        marker="^",
        markersize=3,
        color=colors[module],
    )
ax3.set_xlabel("Number of Atributes", fontsize=12)
ax3.set_ylabel("Serialization Time (seconds)", fontsize=12)
ax3.set_title(
    "Serialization Time by Number of Atributes", fontsize=14, fontweight="bold"
)
ax3.legend(loc="upper left")
ax3.grid(True, alpha=0.3)
ax3.set_xscale("log")
ax3.set_yscale("log")
ax3.set_xlim(left=0.9)

plt.tight_layout()
plt.savefig("results/benchmark_plots.png", dpi=300, bbox_inches="tight")
plt.show()

# Additional analysis: Create a comparison bar plot for specific argument counts
fig2, axes2 = plt.subplots(1, 3, figsize=(15, 5))
fig2.suptitle(
    "Performance Comparison at Different Argument Counts",
    fontsize=14,
    fontweight="bold",
)

argument_counts = [1, 10, 100, 500, 1000]
for idx, n_args in enumerate(argument_counts):
    if idx < 3:  # Only create 3 subplots
        ax = axes2[idx]
        subset = df[df["n_args"] == n_args]

        x_pos = np.arange(len(subset))
        ax.bar(
            x_pos,
            subset["t_creation"],
            width=0.3,
            label="Creation",
            alpha=0.7,
            color="#3498db",
        )
        ax.bar(
            x_pos + 0.3,
            subset["t_serialization"],
            width=0.3,
            label="Serialization",
            alpha=0.7,
            color="#e74c3c",
        )

        ax.set_xlabel("Module")
        ax.set_ylabel("Time (seconds)")
        ax.set_title(f"{n_args} Atributes")
        ax.set_xticks(x_pos + 0.15)
        ax.set_xticklabels(subset["m_name"])
        ax.legend()
        ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("results/benchmark_bar_comparison.png", dpi=300, bbox_inches="tight")
plt.show()

# Create a performance ratio analysis
print("\n" + "=" * 60)
print("PERFORMANCE ANALYSIS")
print("=" * 60)

# Calculate average ratios
for metric in ["t_creation", "t_serialization", "mem"]:
    print(f"\n{metric.upper()} RATIOS (relative to msgspec):")
    msgspec_avg = df[df["m_name"] == "msgspec"][metric].mean()
    pydantic_avg = df[df["m_name"] == "pydantic"][metric].mean()
    dataclass_avg = df[df["m_name"] == "dataclass"][metric].mean()

    print(f"  pydantic/msgspec: {pydantic_avg / msgspec_avg:.2f}x")
    print(f"  dataclass/msgspec: {dataclass_avg / msgspec_avg:.2f}x")

# Create a heatmap of correlations
fig3, ax = plt.subplots(figsize=(10, 6))
correlation_data = df[["n_args", "t_creation", "t_serialization", "mem"]].copy()
correlation_data["t_total"] = (
    correlation_data["t_creation"] + correlation_data["t_serialization"]
)
correlation_matrix = correlation_data.corr()

sns.heatmap(
    correlation_matrix,
    annot=True,
    cmap="coolwarm",
    center=0,
    ax=ax,
    fmt=".2f",
    square=True,
    linewidths=1,
)
ax.set_title("Correlation Between Metrics", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig("results/correlation_heatmap.png", dpi=300, bbox_inches="tight")
plt.show()

# Create efficiency plots (time per argument)
fig4, axes4 = plt.subplots(1, 2, figsize=(12, 5))
fig4.suptitle(
    "Efficiency Analysis: Time per Additional Argument", fontsize=14, fontweight="bold"
)

for module in df["m_name"].unique():
    module_data = df[df["m_name"] == module].sort_values("n_args")

    # Calculate incremental cost
    t_creation_per_arg = module_data["t_creation"] / module_data["n_args"]
    t_serialization_per_arg = module_data["t_serialization"] / module_data["n_args"]

    axes4[0].plot(
        module_data["n_args"],
        t_creation_per_arg,
        label=module,
        linewidth=2,
        color=colors[module],
    )
    axes4[1].plot(
        module_data["n_args"],
        t_serialization_per_arg,
        label=module,
        linewidth=2,
        color=colors[module],
    )

axes4[0].set_xlabel("Number of Atributes")
axes4[0].set_ylabel("Time per Argument (seconds)")
axes4[0].set_title("Creation Time Efficiency")
axes4[0].legend()
axes4[0].grid(True, alpha=0.3)
axes4[0].set_xscale("log")
axes4[0].set_yscale("log")

axes4[1].set_xlabel("Number of Atributes")
axes4[1].set_ylabel("Time per Argument (seconds)")
axes4[1].set_title("Serialization Time Efficiency")
axes4[1].legend()
axes4[1].grid(True, alpha=0.3)
axes4[1].set_xscale("log")
axes4[1].set_yscale("log")

plt.tight_layout()
plt.savefig("results/efficiency_analysis.png", dpi=300, bbox_inches="tight")
plt.show()

print("\n" + "=" * 60)
print("All plots have been saved to the 'results' directory:")
print("  - benchmark_plots.png (main comparison)")
print("  - benchmark_bar_comparison.png (bar chart comparison)")
print("  - correlation_heatmap.png (correlation analysis)")
print("  - efficiency_analysis.png (efficiency metrics)")
print("=" * 60)
