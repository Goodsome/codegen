from enum import Enum


class AssignmentFlavor(Enum):

    NONE = "none"
    LITERAL = "literal"
    SYMBOL = "symbol"
    CALL = "call"
    DICT = "dict"
    LIST = "list"
    RAW_CODE = "raw_code"
    CODE = "code"



class FunctionType(Enum):

    CLASS_METHOD = "class_method"

    STATIC_METHOD = "static_method"

    INSTANCE_METHOD = "instance_method"

    FUNCTION = "function"


class FieldFlavor(Enum):

    PYDANTIC = "pydantic"

    DATACLASS = "dataclass"
