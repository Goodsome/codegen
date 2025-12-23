"""
Kind: ValueObject
Name: ImportSpec
Description: Represents an import statement in a Python module.
"""

from pydantic import Field

from codegen.domain.shared.models import ValueObject


class ImportSpec(ValueObject):
    """Represents an import statement in a Python module."""

    module: str
    name: str
    alias: str = Field(default="")
