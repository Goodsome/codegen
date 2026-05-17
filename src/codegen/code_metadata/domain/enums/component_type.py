from enum import Enum
from .architecture_layer import ArchitectureLayer

class ComponentType(Enum):
    CORE = ("core", "core", ArchitectureLayer.DOMAIN)
    AGGREGATE = ("aggregate", "aggregates", ArchitectureLayer.DOMAIN)
    ENTITY = ("entity", "entities", ArchitectureLayer.DOMAIN)
    VALUE_OBJECT = ("value_object", "value_objects", ArchitectureLayer.DOMAIN)
    ENUM = ("enum", "enums", ArchitectureLayer.DOMAIN)
    DOMAIN_SERVICE = ("domain_service", "services", ArchitectureLayer.DOMAIN)
    DOMAIN_PORT = ("domain_port", "ports", ArchitectureLayer.DOMAIN)
    DOMAIN_EVENT = ("domain_event", "events", ArchitectureLayer.DOMAIN)
    DOMAIN_EXCEPTION = ("domain_exception", "exceptions", ArchitectureLayer.DOMAIN)
    REPOSITORY = ("repository", "repositories", ArchitectureLayer.DOMAIN)

    USE_CASE = ("use_case", "use_cases", ArchitectureLayer.APPLICATION)
    APP_PORT = ("app_port", "ports", ArchitectureLayer.APPLICATION)
    APP_SERVICE = ("app_service", "services", ArchitectureLayer.APPLICATION)
    
    IMPLEMENTATION = ("implementation", "implementations", ArchitectureLayer.INFRASTRUCTURE)
    
    CLI_COMMAND = ("cli_command", "cli", ArchitectureLayer.INTERFACES)
    MCP_TOOL = ("mcp_tool", "mcp", ArchitectureLayer.INTERFACES)
    HTTP_ENDPOINT = ("http_endpoint", "http", ArchitectureLayer.INTERFACES)

    def __new__(cls, value: str, dir_name: str, layer: ArchitectureLayer):
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, value: str, dir_name: str, layer: ArchitectureLayer):
        self.dir_name = dir_name
        self.layer = layer
