from enum import Enum


class ContainerType(Enum):

    NONE = "none"

    LIST = "list"

    SET = "set"

    MAP = "map"

    ITERABLE = "iterable"

    CALLABLE = "callable"

    TYPE = "type"


class PrimitiveType(Enum):
    """通用原语类型，不依赖具体语言。"""

    STRING = "string"

    INTEGER = "integer"

    FLOAT = "float"

    BOOLEAN = "boolean"

    DATETIME = "datetime"

    UUID = "uuid"

    ANY = "any"
