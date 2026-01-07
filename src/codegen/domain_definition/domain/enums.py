from enum import Enum


class ImplementationType(Enum):
    ADAPTER = "adapter"
    REPOSITORY = "repository"
    CLIENT = "client"
    PROVIDER = "provider"
