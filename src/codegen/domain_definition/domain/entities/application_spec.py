from typing import Self

from codegen.domain_definition.domain.entities.dto_spec import DtoSpec
from codegen.domain_definition.domain.entities.port_spec import PortSpec
from codegen.domain_definition.domain.entities.service_spec import ServiceSpec
from codegen.domain_definition.domain.entities.use_case_spec import UseCaseSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from pydantic import Field
from codegen.shared.domain.core.entity import Entity


class ApplicationSpec(Entity):
    """Specification of an application to be generated."""

    use_cases: list[UseCaseSpec] = Field(default_factory=list)
    ports: list[PortSpec] = Field(default_factory=list)
    services: list[ServiceSpec] = Field(default_factory=list)
    dtos: list[DtoSpec] = Field(default_factory=list)

    def to_package_spec(self: Self) -> PackageSpec:
        """将 ApplicationSpec 转换为 PackageSpec"""
        self.migrate()
        use_case_modules = [uc.to_module_spec() for uc in self.use_cases]
        port_modules = [p.to_module_spec() for p in self.ports]
        use_cases_pkg = PackageSpec.create(name="use_cases", modules=use_case_modules)
        ports_pkg = PackageSpec.create(name="ports", modules=port_modules)
        dtos_pkg = DtoSpec.to_package_spec(self.dtos)
        sub_packages = [use_cases_pkg, ports_pkg, dtos_pkg]
        return PackageSpec.create(
            name="application", sub_packages=sub_packages
        )

    @classmethod
    def from_package_spec(cls: type[Self], package_spec: PackageSpec) -> Self:
        """将 PackageSpec 逆向解析为 ApplicationSpec"""
        use_cases = []
        ports = []
        dtos: list[DtoSpec] = []
        for sub_pkg in package_spec.sub_packages:
            if sub_pkg.name == "use_cases":
                for mod in sub_pkg.modules:
                    if not mod.is_init_module():
                        use_cases.append(UseCaseSpec.from_module_spec(mod))
            elif sub_pkg.name == "ports":
                for mod in sub_pkg.modules:
                    if not mod.is_init_module():
                        ports.append(PortSpec.from_module_spec(mod))
            elif sub_pkg.name == "dtos":
                dtos = DtoSpec.from_package_spec(sub_pkg)
        s = cls(use_cases=use_cases, ports=ports, dtos=dtos)
        s.migrate()
        return s

    def add_use_case(self: Self, use_case: UseCaseSpec) -> Self:
        """Add a UseCaseSpec. Raises ValueError if use_case with same name exists."""
        for uc in self.use_cases:
            if uc.name == use_case.name:
                raise ValueError(
                    f"UseCase '{use_case.name}' already exists in application"
                )
        self.use_cases.append(use_case)
        return self

    def update_use_case(self: Self, use_case: UseCaseSpec) -> Self:
        """Update an existing UseCaseSpec by name. Raises ValueError if not found."""
        for i, uc in enumerate(self.use_cases):
            if uc.name == use_case.name:
                self.use_cases[i] = use_case
                return self
        raise ValueError(f"UseCase '{use_case.name}' not found in application")

    def get_use_case(self: Self, name: str) -> UseCaseSpec:
        """Get a UseCaseSpec by name. Raises ValueError if not found."""
        for uc in self.use_cases:
            if uc.name == name:
                return uc
        raise ValueError(f"UseCase '{name}' not found in application")

    def remove_use_case(self: Self, name: str) -> Self:
        """Remove a UseCaseSpec by name. Returns self for chaining."""
        self.use_cases = [uc for uc in self.use_cases if uc.name != name]
        return self

    def add_port(self: Self, port: PortSpec) -> Self:
        """Add a PortSpec. Raises ValueError if port with same name exists."""
        for p in self.ports:
            if p.name == port.name:
                raise ValueError(f"Port '{port.name}' already exists in application")
        self.ports.append(port)
        return self

    def update_port(self: Self, port: PortSpec) -> Self:
        """Update an existing PortSpec by name. Raises ValueError if not found."""
        for i, p in enumerate(self.ports):
            if p.name == port.name:
                self.ports[i] = port
                return self
        raise ValueError(f"Port '{port.name}' not found in application")

    def get_port(self: Self, name: str) -> PortSpec:
        """Get a PortSpec by name. Raises ValueError if not found."""
        for port in self.ports:
            if port.name == name:
                return port
        raise ValueError(f"Port '{name}' not found in application")

    def remove_port(self: Self, name: str) -> Self:
        """Remove a PortSpec by name. Returns self for chaining."""
        self.ports = [p for p in self.ports if p.name != name]
        return self

    def add_service(self: Self, service: ServiceSpec) -> Self:
        """Add a ServiceSpec. Raises ValueError if service with same name exists."""
        for s in self.services:
            if s.name == service.name:
                raise ValueError(
                    f"Service '{service.name}' already exists in application"
                )
        self.services.append(service)
        return self

    def update_service(self: Self, service: ServiceSpec) -> Self:
        """Update an existing ServiceSpec by name. Raises ValueError if not found."""
        for i, s in enumerate(self.services):
            if s.name == service.name:
                self.services[i] = service
                return self
        raise ValueError(f"Service '{service.name}' not found in application")

    def get_service(self: Self, name: str) -> ServiceSpec:
        """Get a ServiceSpec by name. Raises ValueError if not found."""
        for svc in self.services:
            if svc.name == name:
                return svc
        raise ValueError(f"Service '{name}' not found in application")

    def remove_service(self: Self, name: str) -> Self:
        """Remove a ServiceSpec by name. Returns self for chaining."""
        self.services = [s for s in self.services if s.name != name]
        return self

    def migrate(self: Self) -> None:
        """Collect DTOs from use cases into self.dtos.

        If dtos is already populated, this is a no-op.
        Otherwise, iterates over use_cases, calls collect_dtos(),
        and merges the results into self.dtos.
        """
        if self.dtos:
            return
        for uc in self.use_cases:
            self.dtos.extend(uc.collect_dtos())

    def add_dto(self: Self, dto: DtoSpec) -> Self:
        """Add a DtoSpec. Raises ValueError if dto with same name exists."""
        for d in self.dtos:
            if d.name == dto.name:
                raise ValueError(f"Dto '{dto.name}' already exists in application")
        self.dtos.append(dto)
        return self

    def update_dto(self: Self, dto: DtoSpec) -> Self:
        """Update an existing DtoSpec by name. Raises ValueError if not found."""
        for i, d in enumerate(self.dtos):
            if d.name == dto.name:
                self.dtos[i] = dto
                return self
        raise ValueError(f"Dto '{dto.name}' not found in application")

    def get_dto(self: Self, name: str) -> DtoSpec:
        """Get a DtoSpec by name. Raises ValueError if not found."""
        for d in self.dtos:
            if d.name == name:
                return d
        raise ValueError(f"Dto '{name}' not found in application")

    def remove_dto(self: Self, name: str) -> Self:
        """Remove a DtoSpec by name. Returns self for chaining."""
        self.dtos = [d for d in self.dtos if d.name != name]
        return self
