"""
Kind: ValueObject
Name: Command
Description: Use case command DTO (meta-model).
"""

from codegen.domain.shared.models import ValueObject

from codegen.domain.value_objects.attribute import Attribute

from typing import List


class Command(ValueObject):
    """Use case command DTO (meta-model)."""

    name: str

    attributes: List[Attribute]
