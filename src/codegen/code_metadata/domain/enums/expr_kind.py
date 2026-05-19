from enum import StrEnum, auto

class ExprKind(StrEnum):
    CALL = auto()
    DICT = auto()
    CONSTANT = auto()
    REFERENCE = auto()
    SEQUENCE = auto()
    