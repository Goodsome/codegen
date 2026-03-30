from typing import Callable, Self

from pydantic import Field

from codegen.domain_definition.domain.enums import PortType
from codegen.domain_definition.domain.entities.implementation_spec import (
    ImplementationSpec,
)
from codegen.domain_definition.domain.entities.port_spec import PortSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.models import Entity


class InfrastructureSpec(Entity):
    """Specification of an infrastructure to be generated."""

    implementations: list[ImplementationSpec] = Field(default_factory=list)

    def to_package_spec(
        self,
        port_finder: Callable[[str], PortSpec],
    ) -> PackageSpec:
        """将 InfrastructureSpec 转换为 PackageSpec"""
        module_bags: dict[PortType, list[ModuleSpec]] = {}
        for impl in self.implementations:
            port = port_finder(impl.implements)
            module = impl.to_module_spec(port)
            module_bags.setdefault(port.kind, []).append(module)

        kind_packages: list[PackageSpec] = []
        for kind, tech_modules in module_bags.items():
            if kind is PortType.REPOSITORY:
                pkg_name = "repositories"
            else:
                pkg_name = kind.value.lower() + 's'
            kind_pkg = PackageSpec.create(name=pkg_name, modules=tech_modules)
            kind_packages.append(kind_pkg)

        return PackageSpec.create(name="infrastructure", sub_packages=kind_packages)

    @classmethod
    def from_package_spec(cls, package_spec: PackageSpec) -> "InfrastructureSpec":
        """将 PackageSpec 逆向解析为 InfrastructureSpec"""
        implementations = []
        for kind_pkg in package_spec.sub_packages:
            if kind_pkg.name == "utils":
                continue
            for tech_model in kind_pkg.modules:
                if tech_model.is_init_module():
                    continue
                technology = tech_model.name.split("_")[0]
                implementations.append(
                    ImplementationSpec.from_module_spec(
                        module_spec=tech_model,
                        technology=technology,
                    )
                )

        return cls(implementations=implementations)

    def add_implementation(self, implementation: ImplementationSpec) -> Self:
        """Add an ImplementationSpec. Raises ValueError if implementation with same name exists."""
        for impl in self.implementations:
            if impl.name == implementation.name:
                raise ValueError(f"Implementation '{implementation.name}' already exists in infrastructure")
        self.implementations.append(implementation)
        return self

    def update_implementation(self, implementation: ImplementationSpec) -> Self:
        """Update an existing ImplementationSpec by name. Raises ValueError if not found."""
        for i, impl in enumerate(self.implementations):
            if impl.name == implementation.name:
                self.implementations[i] = implementation
                return self
        raise ValueError(f"Implementation '{implementation.name}' not found in infrastructure")

    def get_implementation(self, name: str) -> ImplementationSpec:
        """Get an ImplementationSpec by name. Raises ValueError if not found."""
        for impl in self.implementations:
            if impl.name == name:
                return impl
        raise ValueError(f"Implementation '{name}' not found in infrastructure")

    def remove_implementation(self, name: str) -> Self:
        """Remove an ImplementationSpec by name. Returns self for chaining."""
        self.implementations = [impl for impl in self.implementations if impl.name != name]
        return self

