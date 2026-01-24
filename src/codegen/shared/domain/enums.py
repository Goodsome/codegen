from enum import Enum


class ContainerType(Enum):
    NONE = "none"       # 单值 (默认)
    LIST = "list"       # 列表/数组
    SET = "set"         # 集合 (无序不重复)
    MAP = "map"


class PrimitiveType(Enum):
    """
    通用原语类型，不依赖具体语言。
    """
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    UUID = "uuid"
    ANY = "any"         # 逃生舱，尽量少用

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls._value2member_map_
