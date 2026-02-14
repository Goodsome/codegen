from enum import Enum


class PortType(Enum):

    ADAPTER = "adapter"

    REPOSITORY = "repository"

    CLIENT = "client"

    PROVIDER = "provider"


class MappingDirection(Enum):

    ONE_WAY = "one_way"

    TWO_WAY = "two_way"


class UseCaseKind(Enum):

    COMMAND = "command"

    QUERY = "query"


class TestMockStrategy(Enum):

    UNITTEST = "unittest"

    PYTEST = "pytest"
