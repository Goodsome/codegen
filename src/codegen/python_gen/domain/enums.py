from enum import Enum


class AssignmentFlavor(Enum):

    NONE = "none"

    LITERAL = "literal"

    PYDANTIC_FIELD = "pydantic_field"

    DATACLASS_FIELD = "dataclass_field"


class FunctionType(Enum):

    CLASS_METHOD = "class_method"

    STATIC_METHOD = "static_method"

    INSTANCE_METHOD = "instance_method"

    FUNCTION = "function"


class FieldFlavor(Enum):

    PYDANTIC = "pydantic"

    DATACLASS = "dataclass"
