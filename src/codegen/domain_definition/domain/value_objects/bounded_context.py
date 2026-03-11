from functools import cached_property
from typing import Any

from pydantic import Field

from codegen.domain_definition.domain.value_objects.application_spec import (
    ApplicationSpec,
)
from codegen.domain_definition.domain.value_objects.domain_spec import DomainSpec
from codegen.domain_definition.domain.value_objects.infrastructure_spec import (
    InfrastructureSpec,
)
from codegen.domain_definition.domain.value_objects.config_spec import ConfigSpec
from codegen.domain_definition.domain.value_objects.container_spec import ContainerSpec
from codegen.domain_definition.domain.value_objects.port_spec import PortSpec
from codegen.domain_definition.domain.value_objects.interface_spec import InterfaceSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.models import ValueObject


class BoundedContext(ValueObject):
    """A logical boundary within the system."""

    name: PascalString
    description: str = Field(default_factory=str)
    domain: DomainSpec = Field(default_factory=DomainSpec)
    application: ApplicationSpec = Field(default_factory=ApplicationSpec)
    infrastructure: InfrastructureSpec = Field(default_factory=InfrastructureSpec)
    config: ConfigSpec | None = Field(default=None)
    container: ContainerSpec | None = Field(default=None)
    interfaces: InterfaceSpec | None = Field(default=None)

    @classmethod
    def create(
        cls: Any,
        name: str,
        description: str = "",
        domain: DomainSpec | None = None,
        application: ApplicationSpec | None = None,
        infrastructure: InfrastructureSpec | None = None,
        config: ConfigSpec | None = None,
        container: ContainerSpec | None = None,
        interfaces: InterfaceSpec | None = None,
    ) -> Any:

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
            config=config,
            container=container,
            interfaces=interfaces,
        )

    @cached_property
    def port_index(
        self,
    ) -> dict[str, PortSpec]:

        return {port.name: port for port in self.domain.ports + self.application.ports}

    def get_port_spec(self, port_name: str) -> PortSpec:

        if port_name not in self.port_index:
            raise ValueError(f"Port {port_name} not found in {self.name}")
        return self.port_index[port_name]

