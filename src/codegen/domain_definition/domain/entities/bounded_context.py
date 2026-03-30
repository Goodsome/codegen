from functools import cached_property
from typing import Any, Self

from pydantic import Field

from codegen.domain_definition.domain.entities.application_spec import (
    ApplicationSpec,
)
from codegen.domain_definition.domain.entities.domain_spec import DomainSpec
from codegen.domain_definition.domain.entities.infrastructure_spec import (
    InfrastructureSpec,
)
from codegen.domain_definition.domain.entities.config_spec import ConfigSpec
from codegen.domain_definition.domain.entities.container_spec import ContainerSpec
from codegen.domain_definition.domain.value_objects.port_binding import PortBinding
from codegen.domain_definition.domain.entities.port_spec import PortSpec
from codegen.domain_definition.domain.entities.interface_spec import InterfaceSpec
from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.models import Entity


class BoundedContext(Entity):
    """A logical boundary within the system."""

    name: PascalString
    description: str = Field(default_factory=str)
    domain: DomainSpec = Field(default_factory=DomainSpec)
    application: ApplicationSpec = Field(default_factory=ApplicationSpec)
    infrastructure: InfrastructureSpec = Field(default_factory=InfrastructureSpec)
    interfaces: InterfaceSpec = Field(default_factory=InterfaceSpec)
    config: ConfigSpec | None = Field(default=None)
    container: ContainerSpec | None = Field(default=None)

    def to_package_spec(self, project_name: str = "") -> PackageSpec:
        """Convert this BoundedContext to a PackageSpec."""
        domain_pkg = self.domain.to_package_spec()
        application_pkg = self.application.to_package_spec()
        class_specs: dict[str, ClassSpec] = {}
        self._collect_class_specs_in_ports(class_specs, domain_pkg)
        self._collect_class_specs_in_ports(class_specs, application_pkg)
        infrastructure_pkg = self.infrastructure.to_package_spec(
            port_finder=self.get_port_spec,
        )

        modules: list[ModuleSpec] = []
        sub_packages: list[PackageSpec] = [domain_pkg, application_pkg, infrastructure_pkg]

        # Add shared models for Shared context
        if self.name == "Shared":
            modules.append(ModuleSpec.create_shared_models())
            modules.append(ModuleSpec.create_shared_events())

        # Generate config module if context has config
        if self.config:
            config_module = self.config.to_module_spec(
                class_name=f"{self.name}Settings"
            )
            modules.append(config_module)

        # Generate container module
        container_spec = self.container
        if not container_spec:
            bindings: list[PortBinding] = []
            seen_ports = set()
            for impl in self.infrastructure.implementations:
                if impl.implements not in seen_ports:
                    bindings.append(PortBinding(port=impl.implements, implementation=impl.name))
                    seen_ports.add(impl.implements)
            container_spec = ContainerSpec(bindings=bindings)

        container_module = container_spec.to_module_spec(
            context=self, class_name="Container"
        )
        modules.append(container_module)

        # Generate interfaces package if context has interfaces
        if self.interfaces:
            interfaces_pkg = self.interfaces.to_package_spec(
                context_name=str(self.name),
                use_cases=self.application.use_cases,
                project_name=project_name,
            )
            sub_packages.append(interfaces_pkg)

        return PackageSpec.create(
            name=self.name,
            sub_packages=sub_packages,
            modules=modules,
        )

    def _collect_class_specs_in_ports(
        self, class_specs: dict[str, ClassSpec], package_spec: PackageSpec
    ) -> None:
        """Recursively collect class specs from ports packages."""

        if package_spec.name == "ports":
            class_specs.update(package_spec.collect_class_spec())
        else:
            for pkg in package_spec.sub_packages:
                self._collect_class_specs_in_ports(class_specs, pkg)

    @classmethod
    def from_package_spec(cls, package_spec: PackageSpec) -> Self:
        """Create a BoundedContext from a PackageSpec."""

        domain = None
        application = None
        infrastructure = None
        interfaces = None

        # First pass: parse domain, application, infrastructure
        for pkg in package_spec.sub_packages:
            if pkg.name == "domain":
                domain = DomainSpec.from_package_spec(pkg)
            elif pkg.name == "application":
                application = ApplicationSpec.from_package_spec(pkg)
            elif pkg.name == "infrastructure":
                infrastructure = InfrastructureSpec.from_package_spec(pkg)

        # Get use_cases from application for interface parsing
        use_cases = application.use_cases if application else []

        # Second pass: parse interfaces using use_cases
        for pkg in package_spec.sub_packages:
            if pkg.name == "interfaces":
                interfaces = InterfaceSpec.from_package_spec(pkg, use_cases)

        return cls.create(
            name=package_spec.name,
            domain=domain,
            application=application,
            infrastructure=infrastructure,
            interfaces=interfaces,
        )

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
        if interfaces is None:
            interfaces = InterfaceSpec()
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

    def update(self, description: str | None = None) -> None:
        """Update scalar metadata fields. Preserves internal structure."""
        if description is not None:
            self.description = description

    def get_port_spec(self, port_name: str) -> PortSpec:

        if port_name not in self.port_index:
            raise ValueError(f"Port {port_name} not found in {self.name}")
        return self.port_index[port_name]

