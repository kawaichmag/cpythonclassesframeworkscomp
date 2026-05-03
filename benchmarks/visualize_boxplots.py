from pathlib import Path

import matplotlib.pyplot as plt


RESULT_DIR = Path(__file__).parent / "results"
PLOT_DIR = Path(__file__).parent / "plots"

PLOT_DIR.mkdir(exist_ok=True)


def load_raw_values(log_file: Path):
    data = {}

    with open(log_file, "r", encoding="utf-8") as file:
        for line in file:
            if "INFO" not in line:
                continue

            metric = line.split("|")[-1].split(":")[0].strip()

            value = float(line.split(":")[-1].strip())

            data.setdefault(metric, [])
            data[metric].append(value)

    return data


def prettify_label(label: str):
    return (
        label.replace("serialize", "ser")
        .replace("deserialize", "deser")
        .replace("dataclass", "dc")
        .replace("pydantic", "pd")
        .replace("msgspec", "ms")
    )


def create_boxplot(log_filename: str):

    log_path = RESULT_DIR / log_filename

    values = load_raw_values(log_path)

    labels = []
    datasets = []

    for key, value in values.items():
        labels.append(prettify_label(key))
        datasets.append(value)

    fig, ax = plt.subplots(figsize=(14, 8))

    ax.boxplot(datasets, patch_artist=True)

    ax.set_xticks(range(1, len(labels) + 1))

    ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=10)

    ax.set_title(f"Benchmark: {log_path.stem}", fontsize=18, pad=20)

    ax.set_ylabel("Время / Память", fontsize=13)

    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    output = PLOT_DIR / f"{log_path.stem}_boxplot.png"

    plt.savefig(output, dpi=300, bbox_inches="tight")

    plt.close()

    print(f"График сохранён: {output}")


if __name__ == "__main__":
    create_boxplot("creation.log")
    create_boxplot("serialization.log")
    create_boxplot("serialization_wt_gc.log")
    create_boxplot("memory.log")
    create_boxplot("real_cases.log")
