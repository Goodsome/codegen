from enum import StrEnum, auto


class ExprContext(StrEnum):
    LOAD = auto()
    STORE = auto()
    DEL = auto()
