"""
Kind: ValueObject
Name: MetaInfrastructureAdapter
Description: Specification of an infrastructure adapter to be generated.
"""
from pydantic import Field

from codegen.domain.shared.models import ValueObject

from typing import Any, Dict


class MetaInfrastructureAdapter(ValueObject):
    """Specification of an infrastructure adapter to be generated."""

    name: str

    description: str = Field(default="")

    implements: str

    config: Dict[str, Any]
