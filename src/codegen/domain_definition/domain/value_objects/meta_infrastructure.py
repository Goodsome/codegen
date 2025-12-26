from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.meta_infrastructure_adapter import (
    MetaInfrastructureAdapter,
)
from pydantic import Field


class MetaInfrastructure(ValueObject):
    """Specification of an infrastructure to be generated."""

    adapters: list[MetaInfrastructureAdapter] = Field(default_factory=list)
