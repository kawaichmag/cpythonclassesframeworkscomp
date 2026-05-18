import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Normalize for better visualization
from sklearn.preprocessing import MinMaxScaler

# Set style
plt.style.use("seaborn-v0_8-darkgrid")
sns.set_palette("husl")

# Read the CSV file
csv_file = "results/json_type_comparison.csv"
df = pd.read_csv(csv_file)

print("JSON Type Comparison Results")
print("=" * 80)
print(df.to_string())

# ============================================================================
# Figure 1: Serialization time by type category
# ============================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle(
    "JSON Serialization Performance by Data Type", fontsize=16, fontweight="bold"
)

# 1. Serialization Time
ax1 = axes[0, 0]
categories = df.groupby("type_category")
colors = {
    "Primitive": "#3498db",
    "Collections": "#2ecc71",
    "Complex": "#e74c3c",
    "Special": "#f39c12",
}

for category, group in df.groupby("type_category"):
    bars = ax1.bar(
        group["specific_type"],
        group["serialization_time"],
        label=category,
        alpha=0.7,
        color=colors.get(category, "#95a5a6"),
    )
ax1.set_xlabel("Data Type", fontsize=11)
ax1.set_ylabel("Serialization Time (seconds)", fontsize=11)
ax1.set_title("Serialization Time by Type", fontsize=12, fontweight="bold")
ax1.tick_params(axis="x", rotation=45)
ax1.legend()
ax1.grid(True, alpha=0.3, axis="y")

# 2. Deserialization Time
ax2 = axes[0, 1]
for category, group in df.groupby("type_category"):
    ax2.bar(
        group["specific_type"],
        group["deserialization_time"],
        label=category,
        alpha=0.7,
        color=colors.get(category, "#95a5a6"),
    )
ax2.set_xlabel("Data Type", fontsize=11)
ax2.set_ylabel("Deserialization Time (seconds)", fontsize=11)
ax2.set_title("Deserialization Time by Type", fontsize=12, fontweight="bold")
ax2.tick_params(axis="x", rotation=45)
ax2.legend()
ax2.grid(True, alpha=0.3, axis="y")

# 3. Serialized Size
ax3 = axes[1, 0]
for category, group in df.groupby("type_category"):
    ax3.bar(
        group["specific_type"],
        group["serialized_size_mb"],
        label=category,
        alpha=0.7,
        color=colors.get(category, "#95a5a6"),
    )
ax3.set_xlabel("Data Type", fontsize=11)
ax3.set_ylabel("Serialized Size (MB)", fontsize=11)
ax3.set_title("Serialized Size by Type", fontsize=12, fontweight="bold")
ax3.tick_params(axis="x", rotation=45)
ax3.legend()
ax3.grid(True, alpha=0.3, axis="y")

# 4. Speed (MB/s)
ax4 = axes[1, 1]
for category, group in df.groupby("type_category"):
    ax4.bar(
        group["specific_type"],
        group["speed_mb_per_sec"],
        label=category,
        alpha=0.7,
        color=colors.get(category, "#95a5a6"),
    )
ax4.set_xlabel("Data Type", fontsize=11)
ax4.set_ylabel("Speed (MB/s)", fontsize=11)
ax4.set_title("Serialization Speed by Type", fontsize=12, fontweight="bold")
ax4.tick_params(axis="x", rotation=45)
ax4.legend()
ax4.grid(True, alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig("results/json_type_comparison.png", dpi=300, bbox_inches="tight")
plt.show()

# ============================================================================
# Figure 2: Heatmap for all metrics
# ============================================================================
fig2, ax2 = plt.subplots(figsize=(12, 8))
heatmap_data = df.set_index("specific_type")[
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

# For speed, higher is better, so invert
heatmap_normalized["speed_mb_per_sec"] = 1 - heatmap_normalized["speed_mb_per_sec"]

sns.heatmap(
    heatmap_normalized,
    annot=heatmap_data,
    fmt=".2f",
    cmap="RdYlGn_r",
    center=0.5,
    ax=ax2,
    cbar_kws={"label": "Performance (green = better)"},
)
ax2.set_title(
    "JSON Type Performance Heatmap\n(Green = Better Performance)",
    fontsize=14,
    fontweight="bold",
)
plt.tight_layout()
plt.savefig("results/json_type_heatmap.png", dpi=300, bbox_inches="tight")
plt.show()

# ============================================================================
# Figure 3: String length impact
# ============================================================================
fig3, ax3 = plt.subplots(figsize=(10, 6))
string_types = df[df["specific_type"].str.contains("string", case=False)]
if not string_types.empty:
    x_pos = range(len(string_types))
    ax3.bar(x_pos, string_types["serialization_time"], alpha=0.7, color="#3498db")
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(string_types["specific_type"])
    ax3.set_xlabel("String Type", fontsize=12)
    ax3.set_ylabel("Serialization Time (seconds)", fontsize=12)
    ax3.set_title(
        "String Serialization Performance by Length", fontsize=14, fontweight="bold"
    )
    ax3.grid(True, alpha=0.3, axis="y")

    # Add size annotations
    for i, (idx, row) in enumerate(string_types.iterrows()):
        ax3.text(
            i,
            row["serialization_time"] + 0.01,
            f"{row['serialized_size_mb']:.0f}MB",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    plt.savefig("results/json_string_comparison.png", dpi=300, bbox_inches="tight")
    plt.show()

# ============================================================================
# Figure 4: Collection size impact
# ============================================================================
fig4, ax4 = plt.subplots(figsize=(12, 6))
collection_types = df[df["type_category"] == "Collections"]
if not collection_types.empty:
    sizes = collection_types["specific_type"].str.extract(r"(\w+)_(\w+)")
    collection_types["collection_type"] = sizes[0]
    collection_types["size_category"] = sizes[1]

    # Pivot for grouped bar chart
    pivot_data = collection_types.pivot(
        index="collection_type", columns="size_category", values="serialization_time"
    )
    pivot_data.plot(kind="bar", ax=ax4, alpha=0.7)
    ax4.set_xlabel("Collection Type", fontsize=12)
    ax4.set_ylabel("Serialization Time (seconds)", fontsize=12)
    ax4.set_title(
        "Collection Serialization Time by Size", fontsize=14, fontweight="bold"
    )
    ax4.legend(title="Size Category")
    ax4.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig("results/json_collection_comparison.png", dpi=300, bbox_inches="tight")
    plt.show()

# ============================================================================
# Figure 5: Memory efficiency
# ============================================================================
try:
    mem_df = pd.read_csv("results/json_memory_efficiency.csv")

    fig5, ax5 = plt.subplots(figsize=(10, 6))
    x_pos = range(len(mem_df))
    width = 0.35

    ax5.bar(
        [x - width / 2 for x in x_pos],
        mem_df["memory_data_mb"],
        width,
        label="Raw Data",
        alpha=0.7,
        color="#3498db",
    )
    ax5.bar(
        [x + width / 2 for x in x_pos],
        mem_df["memory_serialized_mb"],
        width,
        label="Serialized",
        alpha=0.7,
        color="#e74c3c",
    )

    ax5.set_xlabel("Data Type", fontsize=12)
    ax5.set_ylabel("Memory Usage (MB)", fontsize=12)
    ax5.set_title(
        "Memory Efficiency: Raw Data vs Serialized", fontsize=14, fontweight="bold"
    )
    ax5.set_xticks(x_pos)
    ax5.set_xticklabels(mem_df["type"])
    ax5.legend()
    ax5.grid(True, alpha=0.3, axis="y")

    # Add compression ratio annotations
    for i, row in mem_df.iterrows():
        ratio = row["compression_ratio"]
        ax5.text(
            i,
            row["memory_serialized_mb"] + 1,
            f"{ratio:.2f}x",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    plt.savefig("results/json_memory_efficiency.png", dpi=300, bbox_inches="tight")
    plt.show()
except Exception:
    print("Memory efficiency data not available")

# ============================================================================
# Print summary statistics
# ============================================================================
print("\n" + "=" * 80)
print("SUMMARY STATISTICS")
print("=" * 80)

print("\nFastest serialization by type category:")
for category in df["type_category"].unique():
    category_data = df[df["type_category"] == category]
    fastest = category_data.loc[category_data["serialization_time"].idxmin()]
    print(
        f"  {category}: {fastest['specific_type']} ({fastest['serialization_time']:.3f}s)"
    )

print("\nSmallest serialized size by type category:")
for category in df["type_category"].unique():
    category_data = df[df["type_category"] == category]
    smallest = category_data.loc[category_data["serialized_size_mb"].idxmin()]
    print(
        f"  {category}: {smallest['specific_type']} ({smallest['serialized_size_mb']:.1f}MB)"
    )

print("\nBest speed by type category:")
for category in df["type_category"].unique():
    category_data = df[df["type_category"] == category]
    fastest = category_data.loc[category_data["speed_mb_per_sec"].idxmax()]
    print(
        f"  {category}: {fastest['specific_type']} ({fastest['speed_mb_per_sec']:.0f}MB/s)"
    )

print("\n" + "=" * 80)
print("Plots saved to 'results' directory:")
print("  - json_type_comparison.png (4-panel bar charts)")
print("  - json_type_heatmap.png (performance heatmap)")
print("  - json_string_comparison.png (string length impact)")
print("  - json_collection_comparison.png (collection size impact)")
print("  - json_memory_efficiency.png (memory usage comparison)")
print("=" * 80)
