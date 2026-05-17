from __future__ import annotations
from enum import StrEnum, auto


class ContainerType(StrEnum):

    NONE = auto()
    LIST = auto()
    SET = auto()
    MAP = auto()
    ITERABLE = auto()
    CALLABLE = auto()
    TYPE = auto()
    CLASS_VAR = auto()


class PrimitiveType(StrEnum):
    """通用原语类型，不依赖具体语言。"""

    STRING = auto()
    INTEGER = auto()
    FLOAT = auto()
    BOOLEAN = auto()
    DATETIME = auto()
    UUID = auto()
    ANY = auto()
    NULL = auto()

    def to_python_builtin(self) -> PythonBuiltinType | None:
        match self:
            case PrimitiveType.STRING:
                return PythonBuiltinType.STR
            case _:
                return None

class PythonBuiltinType(StrEnum):
    EXCEPTION = "Exception"
    STR = "str"

    def to_primitive_type(self) -> PrimitiveType | None:
        match self:
            case PythonBuiltinType.STR:
                return PrimitiveType.STRING
            case _:
                return None
    
