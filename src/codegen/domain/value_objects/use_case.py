"""
Kind: ValueObject
Name: UseCase
Description: Application use case specification (meta-model).
"""

from codegen.domain.shared.models import ValueObject

from codegen.domain.value_objects.command import Command

from codegen.domain.value_objects.result import Result

from typing import List


class UseCase(ValueObject):
    """Application use case specification (meta-model)."""

    name: str

    kind: str

    description: str

    command: Command

    result: Result

    depends_on_services: List[str]

    depends_on_ports: List[str]
