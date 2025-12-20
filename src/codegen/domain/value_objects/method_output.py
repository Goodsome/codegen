"""
Kind: ValueObject
Name: MethodOutput
Description: Specification of the output of a method.
"""

from codegen.domain.shared.models import ValueObject


class MethodOutput(ValueObject):
    """Specification of the output of a method."""

    type: str
