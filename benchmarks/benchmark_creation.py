import timeit

from models import DataclassUser
from models import PydanticUser
from models import MsgspecUser
from logger_config import create_logger

logger = create_logger("creation", "creation.log")

ITERATIONS = 100000


def benchmark_dataclass():
    DataclassUser(id=1, name="Alex", age=25, email="alex@test.com")


def benchmark_pydantic():
    PydanticUser(id=1, name="Alex", age=25, email="alex@test.com")


def benchmark_msgspec():
    MsgspecUser(id=1, name="Alex", age=25, email="alex@test.com")


if __name__ == "__main__":
    dc_time = timeit.timeit(benchmark_dataclass, number=ITERATIONS)

    pd_time = timeit.timeit(benchmark_pydantic, number=ITERATIONS)

    ms_time = timeit.timeit(benchmark_msgspec, number=ITERATIONS)

    logger.info(f"dataclass: {dc_time}")
    logger.info(f"pydantic: {pd_time}")
    logger.info(f"msgspec: {ms_time}")

    print("Тест создания объектов завершён")
