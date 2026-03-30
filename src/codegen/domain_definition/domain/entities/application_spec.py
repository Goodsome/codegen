from typing import Self

from codegen.domain_definition.domain.entities.port_spec import PortSpec
from codegen.domain_definition.domain.entities.service_spec import ServiceSpec
from codegen.domain_definition.domain.entities.use_case_spec import UseCaseSpec
from codegen.domain_definition.domain.enums import UseCaseKind
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.domain.value_objects.pascal_string import PascalString
from codegen.shared.models import Entity
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

    def upsert_use_case(
        self,
        name: str,
        kind: str | UseCaseKind,
        description: str = "",
    ) -> Self:
        """Upsert a UseCaseSpec by name."""
        if isinstance(kind, str):
            kind = UseCaseKind(kind)
        for uc in self.use_cases:
            if uc.name == name:
                uc.update_metadata(kind=kind, description=description)
                return self
        new_use_case = UseCaseSpec.create(
            name=name,
            kind=kind,
            inputs=[],
            outputs=[],
            description=description,
        )
        self.use_cases.append(new_use_case)
        return self

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

    def upsert_port(
        self, 
        name: str, 
        kind: str, 
        description: str,
        aggregate: str | None = None,
    ) -> Self:
        """Upsert a PortSpec by name."""
        for port in self.ports:
            if port.name == name:
                port.update_metadata(kind=kind, description=description, aggregate=aggregate)
                return self
        new_port = PortSpec.create(name=PascalString(name), kind=kind, description=description, aggregate=aggregate)
        self.ports.append(new_port)
        return self

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

    def upsert_service(self, name: str, description: str) -> Self:
        """Upsert a ServiceSpec by name."""
        for svc in self.services:
            if svc.name == name:
                svc.update_metadata(description=description)
                return self
        new_service = ServiceSpec(name=PascalString(name), description=description)
        self.services.append(new_service)
        return self

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

