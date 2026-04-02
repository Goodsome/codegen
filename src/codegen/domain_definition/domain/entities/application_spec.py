from typing import Self

from codegen.domain_definition.domain.entities.port_spec import PortSpec
from codegen.domain_definition.domain.entities.service_spec import ServiceSpec
from codegen.domain_definition.domain.entities.use_case_spec import UseCaseSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.domain.core import Entity
from pydantic import Field


class ApplicationSpec(Entity):
    """Specification of an application to be generated."""

    use_cases: list[UseCaseSpec] = Field(default_factory=list)
    ports: list[PortSpec] = Field(default_factory=list)
    services: list[ServiceSpec] = Field(default_factory=list)

    def to_package_spec(self) -> PackageSpec:
        """将 ApplicationSpec 转换为 PackageSpec"""
        use_case_modules = [uc.to_module_spec() for uc in self.use_cases]
        port_modules = [p.to_module_spec() for p in self.ports]

        use_cases_pkg = PackageSpec.create(name="use_cases", modules=use_case_modules)
        ports_pkg = PackageSpec.create(name="ports", modules=port_modules)

        return PackageSpec.create(
            name="application", sub_packages=[use_cases_pkg, ports_pkg]
        )

    @classmethod
    def from_package_spec(cls, package_spec: PackageSpec) -> "ApplicationSpec":
        """将 PackageSpec 逆向解析为 ApplicationSpec"""
        use_cases = []
        ports = []

        for sub_pkg in package_spec.sub_packages:
            if sub_pkg.name == "use_cases":
                for mod in sub_pkg.modules:
                    if not mod.is_init_module():
                        use_cases.append(UseCaseSpec.from_module_spec(mod))
            elif sub_pkg.name == "ports":
                for mod in sub_pkg.modules:
                    if not mod.is_init_module():
                        ports.append(PortSpec.from_module_spec(mod))

        return cls(use_cases=use_cases, ports=ports)

    def add_use_case(self, use_case: UseCaseSpec) -> Self:
        """Add a UseCaseSpec. Raises ValueError if use_case with same name exists."""
        for uc in self.use_cases:
            if uc.name == use_case.name:
                raise ValueError(
                    f"UseCase '{use_case.name}' already exists in application"
                )
        self.use_cases.append(use_case)
        return self

    def update_use_case(self, use_case: UseCaseSpec) -> Self:
        """Update an existing UseCaseSpec by name. Raises ValueError if not found."""
        for i, uc in enumerate(self.use_cases):
            if uc.name == use_case.name:
                self.use_cases[i] = use_case
                return self
        raise ValueError(f"UseCase '{use_case.name}' not found in application")

    def get_use_case(self, name: str) -> UseCaseSpec:
        """Get a UseCaseSpec by name. Raises ValueError if not found."""
        for uc in self.use_cases:
            if uc.name == name:
                return uc
        raise ValueError(f"UseCase '{name}' not found in application")

    def remove_use_case(self, name: str) -> Self:
        """Remove a UseCaseSpec by name. Returns self for chaining."""
        self.use_cases = [uc for uc in self.use_cases if uc.name != name]
        return self

    def add_port(self, port: PortSpec) -> Self:
        """Add a PortSpec. Raises ValueError if port with same name exists."""
        for p in self.ports:
            if p.name == port.name:
                raise ValueError(f"Port '{port.name}' already exists in application")
        self.ports.append(port)
        return self

    def update_port(self, port: PortSpec) -> Self:
        """Update an existing PortSpec by name. Raises ValueError if not found."""
        for i, p in enumerate(self.ports):
            if p.name == port.name:
                self.ports[i] = port
                return self
        raise ValueError(f"Port '{port.name}' not found in application")

    def get_port(self, name: str) -> PortSpec:
        """Get a PortSpec by name. Raises ValueError if not found."""
        for port in self.ports:
            if port.name == name:
                return port
        raise ValueError(f"Port '{name}' not found in application")

    def remove_port(self, name: str) -> Self:
        """Remove a PortSpec by name. Returns self for chaining."""
        self.ports = [p for p in self.ports if p.name != name]
        return self

    def add_service(self, service: ServiceSpec) -> Self:
        """Add a ServiceSpec. Raises ValueError if service with same name exists."""
        for s in self.services:
            if s.name == service.name:
                raise ValueError(
                    f"Service '{service.name}' already exists in application"
                )
        self.services.append(service)
        return self

    def update_service(self, service: ServiceSpec) -> Self:
        """Update an existing ServiceSpec by name. Raises ValueError if not found."""
        for i, s in enumerate(self.services):
            if s.name == service.name:
                self.services[i] = service
                return self
        raise ValueError(f"Service '{service.name}' not found in application")

    def get_service(self, name: str) -> ServiceSpec:
        """Get a ServiceSpec by name. Raises ValueError if not found."""
        for svc in self.services:
            if svc.name == name:
                return svc
        raise ValueError(f"Service '{name}' not found in application")

    def remove_service(self, name: str) -> Self:
        """Remove a ServiceSpec by name. Returns self for chaining."""
        self.services = [s for s in self.services if s.name != name]
        return self
