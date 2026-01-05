from pydantic import Field
from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.meta_implementation import (
    MetaImplementation,
)


class MetaInfrastructure(ValueObject):
    """Specification of an infrastructure to be generated."""

    adapters: list[MetaImplementation] = Field(default_factory=list)
