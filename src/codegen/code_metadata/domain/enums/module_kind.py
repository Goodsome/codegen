from enum import StrEnum, auto


class ModuleKind(StrEnum):
    FILE = auto()
    DIRECTORY = auto()
    EXTERNAL = auto()
