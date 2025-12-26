from codegen.shared.models import ValueObject
from codegen.domain_definition.domain.value_objects.method_spec import MethodSpec
from pydantic import Field


class MetaService(ValueObject):
    """Specification of a domain service to be generated."""

    name: str
    description: str = Field(default_factory=str)
    operations: list[MethodSpec] = Field(default_factory=list)
