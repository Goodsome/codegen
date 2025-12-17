"""
Kind: ValueObject
Name: Aggregate
Description: A domain aggregate.
"""

from codegen.domain.shared.models import ValueObject

from codegen.domain.value_objects.attribute import Attribute

from typing import List


class Aggregate(ValueObject):
    """A domain aggregate."""

    name: str

    description: str

    attributes: List[Attribute]

    behaviors: List[str]
