"""
Kind: ValueObject
Name: MetaService
Description: Specification of a domain service to be generated.
"""

from pydantic import Field

from codegen.domain.shared.models import ValueObject

from codegen.domain.value_objects.method_spec import MethodSpec

from typing import List


class MetaService(ValueObject):
    """Specification of a domain service to be generated."""

    name: str

    description: str

    operations: List[MethodSpec] = Field(default_factory=list)
