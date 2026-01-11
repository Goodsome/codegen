from codegen.shared.domain.value_objects.naming_string import PascalString
from functools import cached_property

from pydantic import Field

from codegen.domain_definition.domain.value_objects.application_spec import (
    ApplicationSpec,
)
from codegen.domain_definition.domain.value_objects.domain_spec import DomainSpec
from codegen.domain_definition.domain.value_objects.infrastructure_spec import (
    InfrastructureSpec,
)
from codegen.domain_definition.domain.value_objects.port_spec import PortSpec
from codegen.shared.models import ValueObject


class BoundedContext(ValueObject):
    """A logical boundary within the system."""

    name: PascalString
    description: str = Field(default_factory=str)
    domain: DomainSpec = Field(default_factory=DomainSpec)
    application: ApplicationSpec = Field(default_factory=ApplicationSpec)
    infrastructure: InfrastructureSpec = Field(default_factory=InfrastructureSpec)

    @classmethod
    def create(
        cls,
        name: str,
        description: str = "",
        domain: DomainSpec | None = None,
        application: ApplicationSpec | None = None,
        infrastructure: InfrastructureSpec | None = None,
    ):
        if domain is None:
            domain = DomainSpec()
        if application is None:
            application = ApplicationSpec()
        if infrastructure is None:
            infrastructure = InfrastructureSpec()
        return cls(
            name=PascalString(name),
            description=description,
            domain=domain,
            application=application,
            infrastructure=infrastructure,
        )

    @cached_property
    def port_index(self) -> dict[str, PortSpec]:
        return {port.name: port for port in self.domain.ports + self.application.ports}

    def get_port_spec(self, port_name: str) -> PortSpec:
        if port_name not in self.port_index:
            raise ValueError(f"Port {port_name} not found in {self.name}")
        return self.port_index[port_name]
