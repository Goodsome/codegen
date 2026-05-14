from enum import StrEnum, auto
    
class GherkinKeyword(StrEnum):
    """Gherkin 语法关键字，用于 BDD 场景步骤的语义标注。"""

    GIVEN = auto()
    WHEN = auto()
    THEN = auto()
    AND = auto()
    BUT = auto()

class ComponentType(StrEnum):
    AGGREGATE = auto()
    ENTITY = auto()
    VALUE_OBJECT = auto()
    ENUM = auto()
    DOMAIN_SERVICE = auto()
    DOMAIN_PORT = auto()
    DOMAIN_EVENT = auto()
    DOMAIN_EXCEPTION = auto()
    REPOSITORY = auto()

    USE_CASE = auto()
    APP_PORT = auto()
    APP_SERVICE = auto()
    
    IMPLEMENTATION = auto()
    
    CLI_COMMAND = auto()
    MCP_TOOL = auto()
    HTTP_ENDPOINT = auto()