from enum import StrEnum, auto


class EdgeType(StrEnum):
    CONTAINS = auto()
    DEFINES_MODULE = auto()
    
    IMPORTS = auto()
    EXPORTS = auto()
    
    INHERITS = auto()
    IMPLEMENTS = auto()

    CALLS = auto()
    READS = auto()
    WRITES = auto()
    
    TYPED_AS = auto()
    RETURNS = auto()
    ACCEPTS = auto()
    