from enum import Enum


class UseCaseKind(Enum):

    COMMAND = "command"

    QUERY = "query"


class ElementType(Enum):
    AGGREGATE = "aggregate"
    ENTITY = "entity"
    VALUE_OBJECT = "value_object"
    ENUM = "enum"
    DOMAIN_SERVICE = "domain_service"
    DOMAIN_PORT = "domain_port"
    DOMAIN_EVENT = "domain_event"
    DOMAIN_EXCEPTION = "domain_exception"
    REPOSITORY = "repository"

    USE_CASE = "use_case"
    APP_PORT = "app_port"
    APP_SERVICE = "app_service"

    IMPLEMENTATION = "implementation"

    CLI_COMMAND = "cli_command"
    MCP_TOOL = "mcp_tool"
    HTTP_ENDPOINT = "http_endpoint"

class AttributeKind(Enum):

    ATTRIBUTE = "attribute"

    DEPENDENCY = "dependency"

    INPUT = "input"

    OUTPUT = "output"
    

class MethodKind(Enum):

    BEHAVIOR = "behavior"

    OPERATION = "operation"

    PRIVATE = "private"
    
    