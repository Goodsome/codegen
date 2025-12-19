"""
Kind: ValueObject
Name: ValueSpec
Description: Specification of a domain value object to be generated.
"""

from codegen.domain.shared.models import ValueObject

from codegen.domain.value_objects.attribute import Attribute

from typing import List


class ValueSpec(ValueObject):
    """Specification of a domain value object to be generated."""

    name: str

    description: str

    attributes: List[Attribute]
