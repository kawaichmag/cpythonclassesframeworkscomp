import tracemalloc
import sys

from models import DataclassUser
from models import PydanticUser
from models import MsgspecUser
from logger_config import create_logger

logger = create_logger("memory", "memory.log")

COUNT = 100000


def test_dataclass():
    return [DataclassUser(1, "Alex", 25, "alex@test.com") for _ in range(COUNT)]


def test_pydantic():
    return [
        PydanticUser(id=1, name="Alex", age=25, email="alex@test.com")
        for _ in range(COUNT)
    ]


def test_msgspec():
    return [MsgspecUser(1, "Alex", 25, "alex@test.com") for _ in range(COUNT)]


def measure(name, func):
    tracemalloc.start()

    data = func()

    current, peak = tracemalloc.get_traced_memory()

    tracemalloc.stop()

    logger.info(f"{name} current:{current}")
    logger.info(f"{name} peak:{peak}")
    logger.info(f"{name} size:{sys.getsizeof(data)}")


if __name__ == "__main__":
    measure("dataclass", test_dataclass)
    measure("pydantic", test_pydantic)
    measure("msgspec", test_msgspec)

    print("Тест памяти завершён")
