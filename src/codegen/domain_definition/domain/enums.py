from enum import Enum


class PortType(Enum):

    ADAPTER = "adapter"

    REPOSITORY = "repository"

    CLIENT = "client"

    PROVIDER = "provider"


class UseCaseKind(Enum):

    COMMAND = "command"

    QUERY = "query"


class ContextNodeType(Enum):
    AGGREAGET = "aggregate"    
    ENTITY = "entity"
    VALUE_OBJECT = "value_object"
    ENUM = "enum"
    DOMAIN_SERVICE = "domain_service"
    DOMAIN_PORT = "domain_port"
    
    USE_CASE = "use_case"
    APP_PORT = "app_port"
    APP_SERVICE = "app_service"
    
    IMPLEMENTATION = "implementation"
    
    CLI_COMMAND = "cli_command"
