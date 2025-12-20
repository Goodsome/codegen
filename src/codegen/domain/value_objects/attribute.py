"""
Kind: ValueObject
Name: Attribute
Description: Standard specification for a class attribute.
"""
from pydantic import Field

from codegen.domain.shared.models import ValueObject


class Attribute(ValueObject):
    """Standard specification for a class attribute."""

    name: str

    type: str

    description: str = Field(default="")

    optional: bool = Field(default=False)

    default: str | None = Field(default=None)
