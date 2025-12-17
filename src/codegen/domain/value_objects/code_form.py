"""
Kind: ValueObject
Name: CodeForm
Description: Single file or Package based generation.
"""

from codegen.domain.shared.models import ValueObject


class CodeForm(ValueObject):
    """Single file or Package based generation."""

    value: str
