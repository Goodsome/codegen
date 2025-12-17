"""
Kind: ValueObject
Name: LayoutStrategy
Description: Strategy for determining file paths.
"""

from codegen.domain.shared.models import ValueObject


class LayoutStrategy(ValueObject):
    """Strategy for determining file paths."""

    name: str
