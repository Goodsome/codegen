from enum import StrEnum, auto


class CodeNodeKind(StrEnum):
    DIRECTORY = auto()
    FILE = auto()
    MODULE = auto()
    CLASS = auto()
    