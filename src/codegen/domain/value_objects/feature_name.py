"""
Kind: ValueObject
Name: FeatureName
Description: Handles snake_case, PascalCase conversions.
"""

from codegen.domain.shared.models import ValueObject


class FeatureName(ValueObject):
    """Handles snake_case, PascalCase conversions."""

    value: str
