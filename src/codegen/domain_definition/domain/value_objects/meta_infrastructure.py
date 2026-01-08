from pydantic import Field
from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.meta_implementation import (
    ImplementationSpec,
)


class InfrastructureSpec(ValueObject):
    """Specification of an infrastructure to be generated."""

    implementations: list[ImplementationSpec] = Field(default_factory=list)
