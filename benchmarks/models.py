from dataclasses import dataclass
from pydantic import BaseModel
import msgspec


@dataclass(slots=True)
class DataclassUser:
    id: int
    name: str
    age: int
    email: str


class PydanticUser(BaseModel):
    id: int
    name: str
    age: int
    email: str


class MsgspecUser(msgspec.Struct):
    id: int
    name: str
    age: int
    email: str
