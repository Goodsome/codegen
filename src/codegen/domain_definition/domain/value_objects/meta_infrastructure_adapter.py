from codegen.shared.models import ValueObject
from typing import Any
from pydantic import Field


class MetaInfrastructureAdapter(ValueObject):
    """Specification of an infrastructure adapter to be generated."""

    name: str
    description: str = Field(default_factory=str)
    implements: str
    config: dict[str, Any] = Field(default_factory=dict)
