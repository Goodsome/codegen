from codegen.domain_definition.domain.value_objects.use_case_spec import UseCaseSpec
from codegen.domain_definition.domain.value_objects.port_spec import PortSpec
from codegen.shared.models import ValueObject
from pydantic import Field


class ApplicationSpec(ValueObject):
    """Specification of an application to be generated."""

    use_cases: list[UseCaseSpec] = Field(default_factory=list)
    ports: list[PortSpec] = Field(default_factory=list)
