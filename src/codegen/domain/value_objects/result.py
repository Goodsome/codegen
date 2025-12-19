"""
Kind: ValueObject
Name: Result
Description: Use case result DTO (meta-model).
"""

from codegen.domain.shared.models import ValueObject

from codegen.domain.value_objects.attribute import Attribute

from typing import List


class Result(ValueObject):
    """Use case result DTO (meta-model)."""

    name: str

    attributes: List[Attribute]
