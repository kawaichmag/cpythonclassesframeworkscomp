from pathlib import Path
import logging
import re


RESULT_DIR = Path(__file__).parent / "results"
RESULT_DIR.mkdir(exist_ok=True)

RUN_CACHE = {}


def get_next_run_index(log_file: Path) -> int:
    if log_file in RUN_CACHE:
        RUN_CACHE[log_file] += 1
        return RUN_CACHE[log_file]

    if not log_file.exists():
        RUN_CACHE[log_file] = 1
        return 1

    pattern = re.compile(r"RUN=(\d+)")

    last_index = 0

    with open(log_file, "r", encoding="utf-8") as file:
        for line in file:
            match = pattern.search(line)

            if match:
                value = int(match.group(1))

                if value > last_index:
                    last_index = value

    RUN_CACHE[log_file] = last_index + 1

    return RUN_CACHE[log_file]


def create_logger(name: str, filename: str):
    log_file = RESULT_DIR / filename

    run_index = get_next_run_index(log_file)

    logger = logging.getLogger(f"{name}_{run_index}")
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(log_file, encoding="utf-8", mode="a")

    formatter = logging.Formatter(
        f"%(asctime)s | RUN={run_index} | %(levelname)s | %(message)s"
    )

    handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(handler)

    logger.propagate = False

    return logger
