"""
Kind: ValueObject
Name: ValueSpec
Description: A domain value object.
"""

from codegen.domain.shared.models import ValueObject

from codegen.domain.value_objects.attribute import Attribute

from typing import List


class ValueSpec(ValueObject):
    """A domain value object."""

    name: str

    description: str

    attributes: List[Attribute]
