from codegen.domain_definition.domain.enums import ImplementationType
from codegen.orchestration.domain.services.implementation_mapper import (
    ImplementationMapper,
)
from codegen.domain_definition.domain.value_objects.meta_infrastructure import (
    MetaInfrastructure,
)
from dataclasses import dataclass, field

from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.module_spec import ModuleSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.shared.domain.services.naming_service import NamingService


@dataclass
class InfrastructureMapper:

    implementation_mapper: ImplementationMapper = field(
        default_factory=ImplementationMapper
    )
    naming_service: NamingService = field(default_factory=NamingService)

    def to_package_spec(
        self,
        infrastructure: MetaInfrastructure,
        ports_class_specs: dict[str, ClassSpec],
    ) -> PackageSpec:
        module_bags: dict[ImplementationType, list[ModuleSpec]] = {}
        for impl in infrastructure.implementations:
            module = self.implementation_mapper.to_module_spec(impl, ports_class_specs)
            module_bags.setdefault(impl.kind, []).append(module)

        kind_packages: list[PackageSpec] = []
        for kind, tech_modules in module_bags.items():
            pkg_name = kind.value.lower()
            kind_pkg = PackageSpec.create(name=pkg_name, modules=tech_modules)
            kind_packages.append(kind_pkg)

        return PackageSpec.create(name="infrastructure", sub_packages=kind_packages)

    def to_infrastructure(self, package_spec: PackageSpec) -> MetaInfrastructure:
        implementations = []
        for kind_pkg in package_spec.sub_packages:
            kind_name = kind_pkg.name
            if kind_name.endswith("s"):
                kind_name = kind_name[:-1]

            for tech_model in kind_pkg.modules:
                if tech_model.is_init_module():
                    continue
                technology = tech_model.name.split("_")[0]
                implementations.append(
                    self.implementation_mapper.to_implementation(
                        module_spec=tech_model,
                        kind=kind_name,
                        technology=technology,
                    )
                )

        return MetaInfrastructure(implementations=implementations)
