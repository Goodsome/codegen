from enum import Enum


class UseCaseKind(Enum):

    COMMAND = "command"

    QUERY = "query"


class AttributeKind(Enum):

    ATTRIBUTE = "attribute"

    DEPENDENCY = "dependency"

    INPUT = "input"

    OUTPUT = "output"
    

class MethodKind(Enum):

    BEHAVIOR = "behavior"

    OPERATION = "operation"

    PRIVATE = "private"
    