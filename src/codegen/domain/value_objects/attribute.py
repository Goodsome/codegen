"""
Kind: ValueObject
Name: Attribute
Description: A property of a domain model.
"""

from codegen.domain.shared.models import ValueObject


class Attribute(ValueObject):
    """A property of a domain model."""

    name: str

    type: str

    description: str
