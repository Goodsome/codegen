from typing import Callable

from pydantic import Field

from codegen.domain_definition.domain.enums import PortType
from codegen.domain_definition.domain.value_objects.implementation_spec import (
    ImplementationSpec,
)
from codegen.domain_definition.domain.value_objects.port_spec import PortSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.models import ValueObject


class InfrastructureSpec(ValueObject):
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

