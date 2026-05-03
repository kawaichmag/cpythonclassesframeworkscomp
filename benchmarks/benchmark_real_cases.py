import timeit
import msgspec

from dataclasses import dataclass
from pydantic import BaseModel

from logger_config import create_logger

logger = create_logger("real_cases", "real_cases.log")

ITERATIONS = 50000

payload = {
    "id": 1,
    "name": "Alex",
    "age": 25,
    "email": "alex@test.com",
    "is_active": True,
    "score": 99.5,
    "roles": ["admin", "user"],
}


@dataclass(slots=True)
class DataclassCase:
    id: int
    name: str
    age: int
    email: str
    is_active: bool
    score: float
    roles: list[str]


class PydanticCase(BaseModel):
    id: int
    name: str
    age: int
    email: str
    is_active: bool
    score: float
    roles: list[str]


class MsgspecCase(msgspec.Struct):
    id: int
    name: str
    age: int
    email: str
    is_active: bool
    score: float
    roles: list[str]


def run_dataclass():
    DataclassCase(**payload)


def run_pydantic():
    PydanticCase(**payload)


def run_msgspec():
    MsgspecCase(**payload)


if __name__ == "__main__":
    dc = timeit.timeit(run_dataclass, number=ITERATIONS)

    pd = timeit.timeit(run_pydantic, number=ITERATIONS)

    ms = timeit.timeit(run_msgspec, number=ITERATIONS)

    logger.info(f"real dataclass: {dc}")
    logger.info(f"real pydantic: {pd}")
    logger.info(f"real msgspec: {ms}")

    print("Тест реальных кейсов завершён")
