import timeit
import json
import msgspec

from dataclasses import asdict

from models import DataclassUser
from models import PydanticUser
from models import MsgspecUser
from logger_config import create_logger

logger = create_logger("serialization", "serialization.log")

ITERATIONS = 100000

encoder = msgspec.json.Encoder()
decoder = msgspec.json.Decoder(type=MsgspecUser)


dc_user = DataclassUser(1, "Alex", 25, "alex@test.com")

pd_user = PydanticUser(id=1, name="Alex", age=25, email="alex@test.com")

ms_user = MsgspecUser(1, "Alex", 25, "alex@test.com")


def serialize_dataclass():
    json.dumps(asdict(dc_user))


def serialize_pydantic():
    pd_user.model_dump_json()


def serialize_msgspec():
    encoder.encode(ms_user)


def deserialize_dataclass():
    payload = json.dumps(asdict(dc_user))
    json.loads(payload)


def deserialize_pydantic():
    payload = pd_user.model_dump_json()
    PydanticUser.model_validate_json(payload)


def deserialize_msgspec():
    payload = encoder.encode(ms_user)
    decoder.decode(payload)


if __name__ == "__main__":
    dc_ser = timeit.timeit(serialize_dataclass, number=ITERATIONS)

    pd_ser = timeit.timeit(serialize_pydantic, number=ITERATIONS)

    ms_ser = timeit.timeit(serialize_msgspec, number=ITERATIONS)

    dc_des = timeit.timeit(deserialize_dataclass, number=ITERATIONS)

    pd_des = timeit.timeit(deserialize_pydantic, number=ITERATIONS)

    ms_des = timeit.timeit(deserialize_msgspec, number=ITERATIONS)

    logger.info(f"dataclass serialize: {dc_ser}")
    logger.info(f"pydantic serialize: {pd_ser}")
    logger.info(f"msgspec serialize: {ms_ser}")

    logger.info(f"dataclass deserialize: {dc_des}")
    logger.info(f"pydantic deserialize: {pd_des}")
    logger.info(f"msgspec deserialize: {ms_des}")

    print("Тест сериализации завершён")
