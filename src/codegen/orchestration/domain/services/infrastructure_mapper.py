from codegen.orchestration.domain.services.implementation_mapper import (
    ImplementationMapper,
)
from codegen.domain_definition.domain.value_objects.meta_infrastructure import (
    MetaInfrastructure,
)
from dataclasses import dataclass, field

from codegen.python_gen.domain.value_objects.class_spec import ClassSpec
from codegen.python_gen.domain.value_objects.package_spec import PackageSpec
from codegen.domain_definition.domain.value_objects.meta_implementation import (
    MetaImplementation,
)


@dataclass
class InfrastructureMapper:

    implementation_mapper: ImplementationMapper = field(
        default_factory=ImplementationMapper
    )

    def to_package_spec(
        self,
        infrastructure: MetaInfrastructure,
        ports_class_specs: dict[str, ClassSpec],
    ) -> PackageSpec:
        adapter_modules = [
            self.implementation_mapper.to_module_spec(impl, ports_class_specs)
            for impl in infrastructure.adapters
        ]
        adapters_pkg = PackageSpec.create(
            name="adapters",
            modules=adapter_modules,
        )

        return PackageSpec.create(name="infrastructure", sub_packages=[adapters_pkg])

    def to_infrastructure(self, package_spec: PackageSpec) -> MetaInfrastructure:
        adapters = []
        for sub_pkg in package_spec.sub_packages:
            if sub_pkg.name == "adapters":
                for mod in sub_pkg.modules:
                    if not mod.is_init_module():
                        adapters.append(
                            self.implementation_mapper.to_implementation(mod)
                        )

        return MetaInfrastructure(adapters=adapters)
