from codegen.domain_definition.domain.value_objects.meta_use_case import UseCaseSpec
from codegen.domain_definition.domain.value_objects.meta_port import PortSpec
from codegen.shared.models import ValueObject
from pydantic import Field


class ApplicationSpec(ValueObject):
    """Specification of an application to be generated."""

    use_cases: list[UseCaseSpec] = Field(default_factory=list)
    ports: list[PortSpec] = Field(default_factory=list)
