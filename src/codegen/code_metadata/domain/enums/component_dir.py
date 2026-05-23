from enum import StrEnum, auto

class ComponentDir(StrEnum):
    CORE = auto()
    AGGREGATES = auto()
    ENTITIES = auto()
    VALUE_OBJECTS = auto()
    ENUMS = auto()
    SERVICES = auto()
    EXCEPTIONS = auto()
    REPOSITORIES = auto()
    IDENTIFIERS = auto()
    