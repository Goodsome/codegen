from enum import StrEnum, auto


class AstTypeParamKind(StrEnum):
    TYPE_VAR = auto()
    TYPE_VAR_TUPLE = auto()
    PARAM_SPEC = auto()
