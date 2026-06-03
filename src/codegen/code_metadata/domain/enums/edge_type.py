from enum import StrEnum, auto


class EdgeType(StrEnum):
    CONTAINS = auto()
    
    IMPORTS = auto()
    
    INHERITS = auto()
    IMPLEMENTS = auto()
    INSTANTIATES = auto()

    CALLS = auto()

    REFERENCES = auto()

    EXPORTS = auto()
    DEFINES_MODULE = auto()
    