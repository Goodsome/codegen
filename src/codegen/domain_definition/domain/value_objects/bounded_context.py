from codegen.shared.domain.value_objects.pascal_string import PascalString
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
from codegen.domain_definition.domain.value_objects.implementation_spec import (
    ImplementationSpec,
)
from codegen.shared.models import ValueObject
from typing import Any
from codegen.domain_definition.domain.value_objects.aggregate_spec import AggregateSpec
from codegen.domain_definition.domain.value_objects.value_object_spec import ValueObjectSpec
from codegen.domain_definition.domain.value_objects.entity_spec import EntitySpec
from codegen.domain_definition.domain.value_objects.enum_spec import EnumSpec
from codegen.domain_definition.domain.value_objects.service_spec import ServiceSpec
from codegen.domain_definition.domain.value_objects.use_case_spec import UseCaseSpec


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

    def add_domain_component(self, component: Any) -> "BoundedContext":
        if isinstance(component, AggregateSpec):
            return self.model_copy(
                update={"domain": self.domain.add_aggregate(component)}
            )
        if isinstance(component, ValueObjectSpec):
            return self.model_copy(
                update={"domain": self.domain.add_value_object(component)}
            )
        if isinstance(component, EnumSpec):
            return self.model_copy(update={"domain": self.domain.add_enum(component)})
        if isinstance(component, EntitySpec):
            return self.model_copy(
                update={"domain": self.domain.add_entity(component)}
            )
        if isinstance(component, ServiceSpec):
            return self.model_copy(
                update={"domain": self.domain.add_service(component)}
            )
        if isinstance(component, PortSpec):
            return self.model_copy(update={"domain": self.domain.add_port(component)})
        raise ValueError(f"Unknown domain component type: {type(component)}")

    def update_domain_component(self, component: Any) -> "BoundedContext":
        if isinstance(component, AggregateSpec):
            return self.model_copy(
                update={"domain": self.domain.update_aggregate(component)}
            )
        if isinstance(component, ValueObjectSpec):
            return self.model_copy(
                update={"domain": self.domain.update_value_object(component)}
            )
        if isinstance(component, EnumSpec):
            return self.model_copy(
                update={"domain": self.domain.update_enum(component)}
            )
        if isinstance(component, EntitySpec):
            return self.model_copy(
                update={"domain": self.domain.update_entity(component)}
            )
        if isinstance(component, ServiceSpec):
            return self.model_copy(
                update={"domain": self.domain.update_service(component)}
            )
        if isinstance(component, PortSpec):
            return self.model_copy(
                update={"domain": self.domain.update_port(component)}
            )
        raise ValueError(f"Unknown domain component type: {type(component)}")

    def delete_domain_component(
        self, name: str, component_type: str
    ) -> "BoundedContext":
        component_type = component_type.lower()
        if component_type == "aggregate":
            return self.model_copy(
                update={"domain": self.domain.delete_aggregate(name)}
            )
        if component_type in ("valueobject", "value_object"):
            return self.model_copy(
                update={"domain": self.domain.delete_value_object(name)}
            )
        if component_type == "enum":
            return self.model_copy(update={"domain": self.domain.delete_enum(name)})
        if component_type == "entity":
            return self.model_copy(update={"domain": self.domain.delete_entity(name)})
        if component_type == "service":
            return self.model_copy(update={"domain": self.domain.delete_service(name)})
        if component_type == "port":
            return self.model_copy(update={"domain": self.domain.delete_port(name)})
        raise ValueError(f"Unknown domain component type: {component_type}")

    def add_application_component(self, component: Any) -> "BoundedContext":
        if isinstance(component, UseCaseSpec):
            return self.model_copy(
                update={"application": self.application.add_use_case(component)}
            )
        if isinstance(component, PortSpec):
            return self.model_copy(
                update={"application": self.application.add_port(component)}
            )
        raise ValueError(f"Unknown application component type: {type(component)}")

    def update_application_component(self, component: Any) -> "BoundedContext":
        if isinstance(component, UseCaseSpec):
            return self.model_copy(
                update={"application": self.application.update_use_case(component)}
            )
        if isinstance(component, PortSpec):
            return self.model_copy(
                update={"application": self.application.update_port(component)}
            )
        raise ValueError(f"Unknown application component type: {type(component)}")

    def delete_application_component(
        self, name: str, component_type: str
    ) -> "BoundedContext":
        component_type = component_type.lower()
        if component_type in ("usecase", "use_case"):
            return self.model_copy(
                update={"application": self.application.delete_use_case(name)}
            )
        if component_type == "port":
            return self.model_copy(
                update={"application": self.application.delete_port(name)}
            )
        raise ValueError(f"Unknown application component type: {component_type}")

    def add_infrastructure_component(self, component: Any) -> "BoundedContext":
        if isinstance(component, ImplementationSpec):
            return self.model_copy(
                update={
                    "infrastructure": self.infrastructure.add_implementation(component)
                }
            )
        raise ValueError(f"Unknown infrastructure component type: {type(component)}")

    def update_infrastructure_component(self, component: Any) -> "BoundedContext":
        if isinstance(component, ImplementationSpec):
            return self.model_copy(
                update={
                    "infrastructure": self.infrastructure.update_implementation(
                        component
                    )
                }
            )
        raise ValueError(f"Unknown infrastructure component type: {type(component)}")

    def delete_infrastructure_component(
        self, name: str, component_type: str
    ) -> "BoundedContext":
        component_type = component_type.lower()
        if component_type == "implementation":
            return self.model_copy(
                update={
                    "infrastructure": self.infrastructure.delete_implementation(name)
                }
            )
        raise ValueError(f"Unknown infrastructure component type: {component_type}")
