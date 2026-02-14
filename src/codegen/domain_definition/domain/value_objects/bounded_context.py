from functools import cached_property
from typing import Any

from pydantic import Field

from codegen.domain_definition.domain.value_objects.aggregate_spec import AggregateSpec
from codegen.domain_definition.domain.value_objects.application_spec import (
    ApplicationSpec,
)
from codegen.domain_definition.domain.value_objects.domain_spec import DomainSpec
from codegen.domain_definition.domain.value_objects.entity_spec import EntitySpec
from codegen.domain_definition.domain.value_objects.enum_spec import EnumSpec
from codegen.domain_definition.domain.value_objects.implementation_spec import (
    ImplementationSpec,
)
from codegen.domain_definition.domain.value_objects.infrastructure_spec import (
    InfrastructureSpec,
)
from codegen.domain_definition.domain.value_objects.port_spec import PortSpec
from codegen.domain_definition.domain.value_objects.service_spec import ServiceSpec
from codegen.domain_definition.domain.value_objects.use_case_spec import UseCaseSpec
from codegen.domain_definition.domain.value_objects.value_object_spec import (
    ValueObjectSpec,
)
from codegen.shared.domain.value_objects.pascal_string import PascalString
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
        cls: Any,
        name: str,
        description: str = "",
        domain: DomainSpec | None = None,
        application: ApplicationSpec | None = None,
        infrastructure: InfrastructureSpec | None = None,
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


    # =================================================================
    # Dispatcher Logic
    # =================================================================

    def _update_domain(self, updater: Any) -> "BoundedContext":
        return self.model_copy(update={"domain": updater(self.domain)})

    def _update_application(self, updater: Any) -> "BoundedContext":
        return self.model_copy(update={"application": updater(self.application)})

    def _update_infrastructure(self, updater: Any) -> "BoundedContext":
        return self.model_copy(update={"infrastructure": updater(self.infrastructure)})

    # Type -> Add Handler
    _ADD_HANDLERS = {
        # Domain
        AggregateSpec: lambda ctx, c: ctx._update_domain(lambda d: d.add_aggregate(c)),
        EntitySpec: lambda ctx, c: ctx._update_domain(lambda d: d.add_entity(c)),
        ValueObjectSpec: lambda ctx, c: ctx._update_domain(lambda d: d.add_value_object(c)),
        EnumSpec: lambda ctx, c: ctx._update_domain(lambda d: d.add_enum(c)),
        ServiceSpec: lambda ctx, c: ctx._update_domain(lambda d: d.add_service(c)),
        PortSpec: lambda ctx, c: ctx._update_domain(lambda d: d.add_port(c)),  # Default to Domain
        # Application
        UseCaseSpec: lambda ctx, c: ctx._update_application(lambda a: a.add_use_case(c)),
        # Infrastructure
        ImplementationSpec: lambda ctx, c: ctx._update_infrastructure(lambda i: i.add_implementation(c)),
    }

    # Type -> Update Handler
    _UPDATE_HANDLERS = {
        # Domain
        AggregateSpec: lambda ctx, c: ctx._update_domain(lambda d: d.update_aggregate(c)),
        EntitySpec: lambda ctx, c: ctx._update_domain(lambda d: d.update_entity(c)),
        ValueObjectSpec: lambda ctx, c: ctx._update_domain(lambda d: d.update_value_object(c)),
        EnumSpec: lambda ctx, c: ctx._update_domain(lambda d: d.update_enum(c)),
        ServiceSpec: lambda ctx, c: ctx._update_domain(lambda d: d.update_service(c)),
        # Application
        UseCaseSpec: lambda ctx, c: ctx._update_application(lambda a: a.update_use_case(c)),
        # Infrastructure
        ImplementationSpec: lambda ctx, c: ctx._update_infrastructure(lambda i: i.update_implementation(c)),
        # PortSpec handled via _update_port_strategy (added below)
    }

    def add_component(self, component: Any) -> "BoundedContext":
        """Add a component to the context using the dispatcher."""
        handler = self._ADD_HANDLERS.get(type(component))
        if not handler:
            raise ValueError(f"Unsupported component type for addition: {type(component).__name__}")
        return handler(self, component)

    def _update_port_strategy(self, component: PortSpec) -> "BoundedContext":
        """Strategy to update port in Domain layer first, then Application layer."""
        try:
            return self._update_domain(lambda d: d.update_port(component))
        except ValueError:
            # Domain layer not found, try Application layer
            return self._update_application(lambda a: a.update_port(component))

    def update_component(self, component: Any) -> "BoundedContext":
        """Update a component to the context using the dispatcher."""
        # Special handling for PortSpec (dual-location)
        if isinstance(component, PortSpec):
            return self._update_port_strategy(component)

        handler = self._UPDATE_HANDLERS.get(type(component))
        if not handler:
            raise ValueError(f"Unsupported component type for update: {type(component).__name__}")
        return handler(self, component)

    # =================================================================
    # Delete Dispatcher
    # =================================================================

    def _delete_port_strategy(self, name: str) -> "BoundedContext":
        """Strategy to delete port from Domain layer first, then Application layer."""
        try:
            return self._update_domain(lambda d: d.delete_port(name))
        except ValueError:
            # Domain layer not found, try Application layer
            # If Application layer also not found, this will naturally raise ValueError
            return self._update_application(lambda a: a.delete_port(name))

    # Type String -> Delete Handler
    _DELETE_HANDLERS = {
        # Domain
        "aggregate": lambda ctx, name: ctx._update_domain(lambda d: d.delete_aggregate(name)),
        "entity": lambda ctx, name: ctx._update_domain(lambda d: d.delete_entity(name)),
        "value_object": lambda ctx, name: ctx._update_domain(lambda d: d.delete_value_object(name)),
        "valueobject": lambda ctx, name: ctx._update_domain(lambda d: d.delete_value_object(name)),
        "enum": lambda ctx, name: ctx._update_domain(lambda d: d.delete_enum(name)),
        "service": lambda ctx, name: ctx._update_domain(lambda d: d.delete_service(name)),
        "port": lambda ctx, name: ctx._delete_port_strategy(name),
        # Application
        "use_case": lambda ctx, name: ctx._update_application(lambda a: a.delete_use_case(name)),
        "usecase": lambda ctx, name: ctx._update_application(lambda a: a.delete_use_case(name)),
        # Infrastructure
        "implementation": lambda ctx, name: ctx._update_infrastructure(lambda i: i.delete_implementation(name)),
    }

    def delete_component(self, name: str, component_type: str) -> "BoundedContext":
        """Delete a component from the context using the dispatcher."""
        type_clean = component_type.lower().replace("-", "_")

        handler = self._DELETE_HANDLERS.get(type_clean)
        if not handler:
            raise ValueError(f"Unknown component type for deletion: {component_type}")

        return handler(self, name)
