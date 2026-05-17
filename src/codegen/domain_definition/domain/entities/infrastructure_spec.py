from typing import Callable, Self

from pydantic import Field

from codegen.domain_definition.domain.entities.implementation_spec import (
    ImplementationSpec,
)
from codegen.domain_definition.domain.entities.infra_mapper_spec import InfraMapperSpec
from codegen.domain_definition.domain.entities.port_spec import PortSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.domain.core import Entity
from codegen.shared.domain.value_objects.pascal_string import PascalString


class InfrastructureSpec(Entity):
    """Specification of an infrastructure to be generated."""

    implementations: list[ImplementationSpec] = Field(default_factory=list)
    mappers: list[InfraMapperSpec] = Field(default_factory=list)

    def to_package_spec(
        self,
        port_finder: Callable[[str], PortSpec],
    ) -> PackageSpec:
        """将 InfrastructureSpec 转换为 PackageSpec"""
        impl_pkg = ImplementationSpec.to_package_spec(
            implementations=self.implementations,
            port_finder=port_finder,
        )
        sub_packages = [impl_pkg]

        return PackageSpec.create(name="infrastructure", sub_packages=sub_packages)

    @classmethod
    def from_package_spec(cls, package_spec: PackageSpec) -> "InfrastructureSpec":
        """将 PackageSpec 逆向解析为 InfrastructureSpec"""
        implementations: list[ImplementationSpec] = []
        mappers: list[InfraMapperSpec] = []
        for kind_pkg in package_spec.sub_packages:
            if kind_pkg.name == "adapters":
                implementations += ImplementationSpec.from_package_spec(kind_pkg)
            elif kind_pkg.name == "repositories":
                implementations += ImplementationSpec.from_package_spec(kind_pkg)
            elif kind_pkg.name == InfraMapperSpec.__pkg_name__:
                mappers += InfraMapperSpec.from_package_spec(kind_pkg)
        return cls(implementations=implementations, mappers=mappers)

    def add_implementation(self, implementation: ImplementationSpec) -> Self:
        """Add an ImplementationSpec. Raises ValueError if implementation with same name exists."""
        for impl in self.implementations:
            if impl.name == implementation.name:
                raise ValueError(
                    f"Implementation '{implementation.name}' already exists in infrastructure"
                )
        self.implementations.append(implementation)
        return self

    def update_implementation(self, implementation: ImplementationSpec) -> Self:
        """Update an existing ImplementationSpec by name. Raises ValueError if not found."""
        for i, impl in enumerate(self.implementations):
            if impl.name == implementation.name:
                self.implementations[i] = implementation
                return self
        raise ValueError(
            f"Implementation '{implementation.name}' not found in infrastructure"
        )

    def get_implementation(self, name: str) -> ImplementationSpec:
        """Get an ImplementationSpec by name. Raises ValueError if not found."""
        for impl in self.implementations:
            if impl.name == PascalString(name):
                return impl
        raise ValueError(f"Implementation '{name}' not found in infrastructure")

    def remove_implementation(self, name: str) -> Self:
        """Remove an ImplementationSpec by name. Returns self for chaining."""
        self.implementations = [
            impl for impl in self.implementations if impl.name != name
        ]
        return self

    def to_test_package_spec(
        self,
        port_finder: Callable[[str], PortSpec],
    ) -> PackageSpec:
        """Create test package for infrastructure with implementations that have rules."""
        pkgs: list[PackageSpec] = []
        for impl in self.implementations:
            port = port_finder(impl.implements)
            impl_pkg = impl.to_test_package_spec(port)
            pkgs.append(impl_pkg)

        return PackageSpec.create(
            name="infrastructure",
            sub_packages=pkgs
        )

    def to_unit_test_package_spec(self) -> PackageSpec:
        pkgs: list[PackageSpec] = []
        pkgs += [m.to_test_package_spec() for m in self.mappers]
        return PackageSpec.create(
            name="infrastructure",
            sub_packages=pkgs
        )

    def load_test_package(self: Self, test_pkg: PackageSpec, port_finder: Callable[[str], PortSpec]) -> Self:
        """Load test package into the infrastructure spec. Returns self for chaining."""
        for pkg in test_pkg.sub_packages:
            if pkg.name == "implementations":
                for impl_pkg in pkg.sub_packages:
                    impl = self.get_implementation(impl_pkg.name)
                    port = port_finder(impl.implements)
                    impl.load_test_package(impl_pkg, port)
            elif pkg.name == InfraMapperSpec.__pkg_name__:
                for mapper_pkg in pkg.sub_packages:
                    mapper = self.get_mapper(mapper_pkg.name)
                    mapper.load_test_package(mapper_pkg)
        return self

    def get_mapper(self, name: str) -> InfraMapperSpec:
        for mapper in self.mappers:
            if mapper.name == PascalString(name):
                return mapper
        raise ValueError(f"Mapper {name} not found")
