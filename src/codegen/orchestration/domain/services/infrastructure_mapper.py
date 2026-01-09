from typing import Callable

from codegen.domain_definition.domain.enums import PortType
from codegen.domain_definition.domain.value_objects.meta_port import PortSpec
from codegen.orchestration.domain.services.implementation_mapper import (
    ImplementationMapper,
)
from codegen.domain_definition.domain.value_objects.meta_infrastructure import (
    InfrastructureSpec,
)
from dataclasses import dataclass, field

from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.domain.services.naming_service import NamingService

from logging import getLogger


logger = getLogger(__name__)


@dataclass
class InfrastructureMapper:

    implementation_mapper: ImplementationMapper = field(
        default_factory=ImplementationMapper
    )
    naming_service: NamingService = field(default_factory=NamingService)

    def to_package_spec(
        self,
        infrastructure: InfrastructureSpec,
        port_finder: Callable[[str], PortSpec],
    ) -> PackageSpec:
        module_bags: dict[PortType, list[ModuleSpec]] = {}
        for impl in infrastructure.implementations:
            port = port_finder(impl.implements)
            module = self.implementation_mapper.to_module_spec(impl, port)
            module_bags.setdefault(port.kind, []).append(module)

        kind_packages: list[PackageSpec] = []
        for kind, tech_modules in module_bags.items():
            pkg_name = kind.value.lower()
            kind_pkg = PackageSpec.create(name=pkg_name, modules=tech_modules)
            kind_packages.append(kind_pkg)

        return PackageSpec.create(name="infrastructure", sub_packages=kind_packages)

    def to_infrastructure(self, package_spec: PackageSpec) -> InfrastructureSpec:
        implementations = []
        for kind_pkg in package_spec.sub_packages:
            for tech_model in kind_pkg.modules:
                if tech_model.is_init_module():
                    continue
                technology = tech_model.name.split("_")[0]
                implementations.append(
                    self.implementation_mapper.to_implementation(
                        module_spec=tech_model,
                        technology=technology,
                    )
                )

        return InfrastructureSpec(implementations=implementations)
