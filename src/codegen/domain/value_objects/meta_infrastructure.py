"""
Kind: ValueObject
Name: MetaInfrastructure
Description: Specification of an infrastructure to be generated.
"""

from pydantic import Field

from codegen.domain.shared.models import ValueObject

from codegen.domain.value_objects.meta_infrastructure_adapter import (
    MetaInfrastructureAdapter,
)

from typing import List


class MetaInfrastructure(ValueObject):
    """Specification of an infrastructure to be generated."""

    adapters: List[MetaInfrastructureAdapter] = Field(default_factory=list)
