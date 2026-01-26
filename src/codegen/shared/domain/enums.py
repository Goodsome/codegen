from enum import Enum


class ContainerType(Enum):

    NONE = "none"

    LIST = "list"

    SET = "set"

    MAP = "map"


class PrimitiveType(Enum):
    """通用原语类型，不依赖具体语言。"""

    STRING = "string"

    INTEGER = "integer"

    FLOAT = "float"

    BOOLEAN = "boolean"

    DATETIME = "datetime"

    UUID = "uuid"

    ANY = "any"
    
    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls._value2member_map_
