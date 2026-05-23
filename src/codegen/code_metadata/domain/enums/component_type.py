from enum import StrEnum, auto

class ComponentType(StrEnum):
    CORE = auto()
    AGGREGATE = auto()
    ENTITY = auto()
    VALUE_OBJECT = auto()
    ENUM = auto()
    DOMAIN_SERVICE = auto()
    DOMAIN_PORT = auto()
    DOMAIN_EVENT = auto()
    DOMAIN_EXCEPTION = auto()
    REPOSITORY = auto()
    IDENTIFIER = auto()

    USE_CASE = auto()
    APP_PORT = auto()
    APP_SERVICE = auto()
    
    IMPLEMENTATION = auto()
    
    CLI_COMMAND = auto()
    MCP_TOOL = auto()
    HTTP_ENDPOINT = auto()

    EXTERNAL = auto()
