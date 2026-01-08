from enum import Enum


class PortType(Enum):
    ADAPTER = "adapter"
    REPOSITORY = "repository"
    CLIENT = "client"
    PROVIDER = "provider"
