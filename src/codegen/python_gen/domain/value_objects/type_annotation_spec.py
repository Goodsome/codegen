"""
Kind: ValueObject
Name: TypeAnnotationSpec
Description: Represents a type annotation.
"""

from codegen.domain.shared.models import ValueObject


class TypeAnnotationSpec(ValueObject):
    """Represents a type annotation."""

    name: str