from enum import StrEnum


class FunctionType(StrEnum):
    CLASS_METHOD = "class_method"
    STATIC_METHOD = "static_method"
    INSTANCE_METHOD = "instance_method"
    FUNCTION = "function"


class FieldFlavor(StrEnum):
    PYDANTIC = "pydantic"
    DATACLASS = "dataclass"
