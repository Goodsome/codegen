from enum import StrEnum, auto


class EdgeType(StrEnum):
    CONTAINS = auto()
    DEFINES_MODULE = auto()
    
    IMPORTS = auto()
    CALLS = auto()
    INHERITS = auto()
    INSTANTIATES = auto()
    
    IMPLEMENTS = auto()


    REFERENCES = auto()
    EXPORTS = auto()
    