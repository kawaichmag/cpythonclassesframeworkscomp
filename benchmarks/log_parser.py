from pathlib import Path
import re
import statistics
import json


RESULT_DIR = Path(__file__).parent / "results"
OUTPUT_DIR = Path(__file__).parent / "processed"

OUTPUT_DIR.mkdir(exist_ok=True)

NUMBER_PATTERN = re.compile(r"([-+]?\d*\.\d+|\d+)$")


def extract_metric(line: str):
    match = NUMBER_PATTERN.search(line.strip())

    if not match:
        return None

    return float(match.group(1))


def parse_log_file(log_path: Path):
    metrics = {}

    with open(log_path, "r", encoding="utf-8") as file:
        for line in file:
            if "INFO" not in line:
                continue

            value = extract_metric(line)

            if value is None:
                continue

            metric_name = line.split("|")[-1].split(":")[0].strip()

            metrics.setdefault(metric_name, [])
            metrics[metric_name].append(value)

    return metrics


def calculate_statistics(values: list[float]):
    if len(values) < 2:
        return {
            "count": len(values),
            "mean": values[0] if values else 0,
            "std": 0,
            "var": 0,
            "min": min(values) if values else 0,
            "max": max(values) if values else 0,
            "median": values[0] if values else 0,
        }

    return {
        "count": len(values),
        "mean": statistics.mean(values),
        "std": statistics.stdev(values),
        "var": statistics.variance(values),
        "min": min(values),
        "max": max(values),
        "median": statistics.median(values),
    }


def process_log(log_filename: str):
    log_path = RESULT_DIR / log_filename

    metrics = parse_log_file(log_path)

    result = {}

    for metric_name, values in metrics.items():
        result[metric_name] = calculate_statistics(values)

    output_file = OUTPUT_DIR / f"{log_path.stem}_stats.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    print(f"Статистика сохранена: {output_file}")


if __name__ == "__main__":
    process_log("creation.log")
    process_log("serialization.log")
    process_log("serialization_wt_gc.log")
    process_log("memory.log")
    process_log("real_cases.log")
