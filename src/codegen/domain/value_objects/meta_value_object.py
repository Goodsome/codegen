"""
Kind: ValueObject
Name: MetaValueObject
Description: Specification of a value object to be generated.
"""

from pydantic import Field
from codegen.domain.shared.models import ValueObject

from codegen.domain.value_objects.attribute import Attribute

from typing import List


class MetaValueObject(ValueObject):
    """Specification of a value object to be generated."""

    name: str

    description: str = Field(default="")

    attributes: List[Attribute]
